# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import asyncio
import functools
import json
import logging
import math
import time
import traceback
from calendar import calendar
from datetime import datetime
from distutils.log import info
from glob import glob
from io import BytesIO
from os import getpid, remove

import alexflipnote
import apscheduler.schedulers.asyncio
import discord
import timeago as timesince
from discord import Embed
from discord.ext import commands
from discord.ext.commands import NoPrivateMessage, when_mentioned_or
from discord.utils import utcnow
from psutil import Process

from lib.db import db
from utils.cache import CacheManager
from utils.help import PaginatedHelpCommand
from utils.http import HTTPSession
from utils.vars import dark_blue, error, green, yellow, invis

BannedUsers = {}


def wrap(type, text):
    return f'```{type}\n{text}```'


def config(filename: str = "config"):
    """ Fetch default config file """
    try:
        with open(f"{filename}.json", encoding='utf8') as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


async def emptyfolder(folder):
    files = glob(folder)
    for f in files:
        remove(f)


class Timer:
    def __init__(self):
        self._start = None
        self._end = None

    def start(self):
        self._start = time.perf_counter()

    def stop(self):
        self._end = time.perf_counter()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __int__(self):
        return round(self.time)

    def __float__(self):
        return self.time

    def __str__(self):
        return str(self.time)

    def __repr__(self):
        return f"<Timer time={self.time}>"

    @property
    def time(self):
        if self._end is None:
            raise ValueError("Timer has not been ended.")
        return self._end - self._start

    # Usage:
    # with Timer() as timer:
    #    # do stuff that takes time here
    #    print("hello")
    # print(f"That took {timer} seconds to do")


def ReportEmbed(ctx, type, body: str, directed_at=None):
    rmby = discord.Embed(color=dark_blue, title=f'***A New {type} Report Came In***')
    rmby.set_author(name=f'{ctx.author.name} Just Reported {directed_at}', icon_url=ctx.author.display_avatar.url)
    # if directed_at:
    #    rmby.add_field(name='Target', value=directed_at)
    rmby.description = body
    return rmby


async def toggle_role(ctx, role_id):
    if any(r.id == role_id for r in ctx.author.roles):
        try:
            await ctx.author.remove_roles(discord.Object(id=role_id))
        except:
            await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
        else:
            await ctx.message.add_reaction('\N{HEAVY MINUS SIGN}')
        finally:
            return

    try:
        await ctx.author.add_roles(discord.Object(id=role_id))
    except:
        await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
    else:
        await ctx.message.add_reaction('\N{HEAVY PLUS SIGN}')


async def check_guild_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def is_dj_or_perms(**perms):
    # will first check for dj role then perms
    perms['deafen_members'] = True
    perms['manage_channels'] = True
    perms['move_members'] = True
    perms['mute_members'] = True
    perms['priority_speaker'] = True
    roles = 'dj', 'Dj', 'DJ'

    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()

        getter = functools.partial(discord.utils.get, ctx.author.roles)
        if any(getter(id=role) is not None if isinstance(role, int) else getter(name=role) is not None for role in
               roles):
            return True
        return await check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def is_mod():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'manage_guild': True})

    return commands.check(pred)


def is_admin():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'administrator': True})

    return commands.check(pred)


def mod_or_permissions(**perms):
    perms['manage_guild'] = True

    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def admin_or_permissions(**perms):
    perms['administrator'] = True

    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def can_handle(ctx, permission: str):
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(ctx.channel, discord.DMChannel) or getattr(ctx.channel.permissions_for(ctx.guild.me), permission)


confi = config()
log = logging.getLogger(__name__)
description = 'Relatively simply awesome bot. Developed by Jake CEO of annoyance#1904'

class EEmbed(discord.Embed):
    def __init__(self, color=0x3DB4FF, fields=(), field_inline=False, **kwargs):
        super().__init__(color=color, **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def minimal(cls, timestamp=None, **kwargs):
        instance = cls(timestamp=timestamp or utcnow(), **kwargs)
        return instance

    @classmethod
    def default(cls, ctx, timestamp=None, **kwargs):
        instance = cls.minimal(timestamp=timestamp or utcnow(), **kwargs)
        instance.set_footer(
            text="Requested by {}".format(ctx.author), icon_url=ctx.author.avatar.url
        )
        return instance
    @classmethod
    def loading(
        cls,
        *,
        emoji='<a:wait:879146899670708234>',
        title="Loading...",
        **kwargs,
    ):
        return cls(title="{} {}".format(emoji, title), **kwargs)


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        return self.bot.session

    def tick(self, opt, label=None):
        lookup = {
            True: '<a:b_yes:879161311353778247>',
            False: '<a:no:879146899322601495>',
            None: '<:graytick:879146777842962454>',
        }
        emoji = lookup.get(opt, '<a:no:879146899322601495>')
        if label is not None:
            return f'{emoji}: {label}'
        return emoji

    async def try_reply(self, content=None, *, mention_author=False, **kwargs):
        """Try reply, if failed do send instead"""
        try:
            action = self.safe_reply
            return await action(content, mention_author=mention_author, **kwargs)
        except BaseException:
            if mention_author:
                content = f"{self.author.mention} " + content if content else ""

            action = self.safe_send
            return await self.safe_send(content, **kwargs)

    async def safe_send(self, content, *, escape_mentions=True, channel=False, **kwargs):
        """Same as send except with some safe guards.
        1) If the message is too long then it sends a file with the results instead.
        2) If ``escape_mentions`` is ``True`` then it escapes mentions.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if channel:
            channel = self.bot.get_channel(channel)
        else:
            channel = self

        if len(content) > 2000:
            fp = BytesIO(content.encode())
            kwargs.pop('file', None)
            return await channel.send(file=discord.File(fp, filename='message_too_long.txt'), **kwargs)
        else:
            return await channel.send(content)

    async def safe_reply(self, content, *, escape_mentions=True, **kwargs):
        return await self.safe_send_reply(
            content, escape_mentions=escape_mentions, type="reply", **kwargs
        )

    async def safe_send_reply(
        self, content, *, escape_mentions=True, type="send", **kwargs
    ):
        action = getattr(self, type)

        if escape_mentions and content is not None:
            content = discord.utils.escape_mentions(content)

        if content is not None and len(content) > 2000:
            fp = BytesIO(content.encode())
            kwargs.pop("file", None)
            return await action(
                file=discord.File(fp, filename="message_too_long.txt"), **kwargs
            )
        else:
            if content is not None:
                kwargs["content"] = content
            return await action(**kwargs)

    async def error(self, error_message):
        e = Embed(color=error)
        e.description = str(error_message)
        return await self.try_reply(embed=e)

    async def success(self, success_message: str = None):
        e = Embed(color=green)
        e.description = str(success_message)
        return await self.try_reply(embed=e)

    async def warn(self, warn_message: str = None):
        e = Embed(color=yellow)
        e.description = str(warn_message)
        return await self.try_reply(embed=e)

    async def invis(self, invis_message):
        e = Embed(color=invis)
        e.description = str(invis_message)
        return await self.try_reply(embed=e)

    async def unknown(self, unknownerror, command):
        e = Embed(color=error, title=command.name)
        e.description = str(unknownerror)
        channel = self.bot.get_channel(867828022752444416)
        await self.try_reply(f'An unknown error happend with {command.name}')
        return await channel.send(embed=e)

    async def report(self, ctx, msg):
        channel = self.bot.get_channel(877724111420391515)
        if len(msg) > 300:
            return self.error('Too Long please keep under 300 characters')
        elif len(msg) < 20:
            return self.warn('Too short please keep over 20 characters')
        e = Embed(color=green)
        e.description = str(msg)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        await channel.send(embed=e)

    @discord.utils.cached_property
    def replied_reference(self):
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

class edoC(commands.AutoShardedBot):
    def __init__(self):
        self.db = None
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.now()
        self.start_time = discord.utils.utcnow()
        allowed_mentions = discord.AllowedMentions(roles=True, everyone=False, users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            presences=True
        )
        super().__init__(command_prefix=when_mentioned_or('~'), description=description,
                         pm_help=None, help_attrs=dict(hidden=True),
                         chunk_guilds_at_startup=False, heartbeat_timeout=150.0,
                         allowed_mentions=allowed_mentions, intents=intents,
                         owner_ids=confi["owners"], case_insensitive=True,
                         command_attrs=dict(hidden=True), help_command=PaginatedHelpCommand(), )
        self.session = HTTPSession(loop=self.loop)
        self.prefix = '~'
        self.process = Process(getpid())
        self.config = config()
        self.tempimgpath = 'data/img/temp/*'
        self.ownerid = 511724576674414600
        self.icons = {}
        self.ready = False
        self.scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()
        self.total_commands_ran = 0
        self.alex_api = alexflipnote.Client(confi['alexflipnote_api'],
                                            loop=self.loop)  # just a example, the client doesn't have to be under bot and loop kwarg is optional
        self.cache = CacheManager()

        # self.blacklist = Config('blacklist.json')

    # async def on_guild_join(self, guild):
    #    if guild.id in self.blacklist:
    #        await guild.leave()

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not can_handle(msg, "send_messages"):
            return

        await self.process_commands(msg)

    async def close(self):
        await self.session.close()
        await super().close()

    def loading_emojis(self):
        emojis = {
            "greenTick": "<a:b_yes:879161309315346582>",
            "redTick": "<a:no:879146899322601495>",
            "plus": "<:plus:882749457932902401>",
            "minus": "<:minus:882749665777438740>",
            "save": "<:save:882749805703618590>",
            'online': '<:online:808613541774360576>',
            'offline': '<:offline:817034738014879845>',
            'idle': '<:idle:817035319165059102>',
            'dnd': '<:dnd:817035352925536307>',
            'boosters': '<:Boosters:814930829461553152>',
            'typing': '<a:typing:884860688164597841>',
            'database': '<:database:857553072909189191>',
            'edoc': '<:edoC:874868276256202782>',
            'loading': '<a:loadshuffle:879146779235471430>'
        }
        self.icons = emojis
        return self.icons
    async def get_or_fetch_member(self, guild, member_id):
        """Looks up a member in cache or fetches if not found.
        Parameters
        -----------
        guild: Guild
            The guild to look in.
        member_id: int
            The member ID to search for.
        Returns
        ---------
        Optional[Member]
            The member or None if not found.
        """

        member = guild.get_member(member_id)
        if member is not None:
            return member

        shard = self.get_shard(guild.shard_id)
        if shard.is_ws_ratelimited():
            try:
                member = await guild.fetch_member(member_id)
            except discord.HTTPException:
                return None
            else:
                return member

        members = await guild.query_members(limit=1, user_ids=[member_id], cache=True)
        if not members:
            return None
        return members[0]

    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        """ The function that activates when boot was completed """
        invite_link_cache = []
        await emptyfolder(self.tempimgpath)
        logschannel = self.get_channel(self.config["edoc_non_critical_logs"])
        # Check if user desires to have something other than online
        status = self.config["status_type"].lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        # Check if user desires to have a different type of activity
        activity = self.config["activity_type"].lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}
        totalmembers = sum(g.member_count for g in self.guilds)

        await self.change_presence(
            activity=discord.Game(
                type=activity_type.get(activity, 3),
                name=f"Watching over {totalmembers} Members spread over {len(self.guilds)} Guilds!\nPrefix: ~"
            ),
            status=status_type.get(status, discord.Status.online)
        )

        if not self.ready:
            self.ready = True
            self.scheduler.start()
            await logschannel.send(f"{self.user} has been booted up")
            # Indicate that the bot has successfully booted up
            print(
                f"Ready: {self.user} | Total members {totalmembers} | Guild count: {len(self.guilds)} | Guilds")
            guilds = {}
            for Server in self.guilds:
                gprefix = db.field('SELECT Prefix FROM guilds WHERE GuildID = ?', Server.id)
                print(
                    f"{Server.id} ~ {Server} ~ {Server.owner} ~ {Server.member_count} ~ Prefix {gprefix}")
            self.loading_emojis()
            await self.fill_cache()
        else:
            print(f"{self.user} Reconnected")
            await logschannel.send(f"{self.user} has been reconnected")

    async def on_command(self, ctx):
        try:
            self.commands_ran[ctx.command.qualified_name] += 1
        except KeyError:
            pass
        self.total_commands_ran += 1
        if ctx.author.id in BannedUsers:
            return
        else:
            blocked = False
        try:
            try:
                try:
                    print(
                        f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content} > Blocked {blocked}")
                    info(f'{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}')
                except AttributeError:
                    print(f"Private message > {ctx.author} > {ctx.message.clean_content} > Blocked {blocked}")
                    info(f'Private message > {ctx.author} ')
                    # {ctx.author} > {ctx.message.clean_content}
            except UnicodeEncodeError:
                try:
                    print(f"{ctx.guild.name} > {ctx.author}")
                    info(f'{ctx.guild.name} > {ctx.author}')
                except AttributeError:
                    print(f"Private message > {ctx.author} >")
                    info(f'Private message > {ctx.author} ')

        except:
            pass

    async def fill_cache(self):
        """Loading up the blacklisted users."""
        #query = 'SELECT * FROM (SELECT guild_id AS snowflake_id, blacklisted  FROM guild_config  UNION ALL SELECT user_id AS snowflake_id, blacklisted  FROM users_data) WHERE blacklisted="TRUE"'
        #cur = await self.db.execute(query)
        #data = await cur.fetchall()
        #self.cache["blacklisted_users"] = {r[0] for r in data} or set()
#
        #"""Loading up premium users."""
        #query = 'SELECT * FROM (SELECT guild_id AS snowflake_id, premium  FROM guild_config  UNION ALL SELECT user_id AS snowflake_id, premium  FROM users_data) WHERE premium="TRUE"'
        #cur = await self.db.execute(query)
        #data = await cur.fetchall()
        #self.cache["premium_users"] = {r[0] for r in data} or set()
#
        #"""Loading up users that have tips enabled"""
        #query = 'SELECT user_id FROM users_data WHERE tips = "TRUE"'
        #cur = await self.db.execute(query)
        #data = await cur.fetchall()
        #self.cache["tips_are_on"] = {r[0] for r in data} or set()
#
        #"""Loading up users that have mentions enabled"""
        #query = 'SELECT user_id FROM users_data WHERE mentions = "TRUE"'
        #cur = await self.db.execute(query)
        #data = await cur.fetchall()
        #self.cache["mentions_are_on"] = {r[0] for r in data} or set()
#
        #"""Loads up all disabled_commands"""
        #query = "SELECT command_name, snowflake_id FROM disabled_commands ORDER BY command_name"
        #cur = await self.db.execute(query)
        #data = await cur.fetchall()
        #self.cache["disabled_commands"] = {
        #    cmd: [r[1] for r in _group]
        #    for cmd, _group in itertools.groupby(data, key=operator.itemgetter(0))
        #}

        self.cache["users"] = {}
        self.cache['afk_users'] = {}
        self.cache["tips_are_on"] = {}
        self.cache["disabled_commands"] = {}
        self.cache["premium_users"] = {}
        self.cache["blacklisted_users"] = {}

def UpdateBlacklist(newblacklist, filename: str = "blacklist"):
    try:
        with open(f"{filename}.json", encoding='utf-8', mode="r+") as file:
            data = json.load(file)
            data.update(newblacklist)
            data.seek(0)
            json.dump(data, file)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


def MakeBlackList(dict, filename: str = "blacklist", ):
    try:
        with open(f"{filename}.json", encoding='utf-8', mode="r+") as file:
            data = json.load(file)
            guilds = {}
            users = {}
            for gid in data['guilds']:
                pass
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


def bold(text: str):
    return f'**{text}**'


def italic(text: str):
    return f'*{text}*'


def bolditalic(text: str):
    return f'***{text}***'


def underline(text: str):
    return f'__{text}__'


def traceback_maker(err, advance: bool = True):
    """ A way to debug your code anywhere """
    _traceback = ''.join(traceback.format_tb(err.__traceback__))
    error = '```py\n{1}{0}: {2}\n```'.format(type(err).__name__, _traceback, err)
    return error if advance else f"{type(err).__name__}: {err}"


def spacefill(len):
    return ' ' * len


def timetext(name):
    """ Timestamp, but in text form """
    return f"{name}_{int(time.time())}.txt"


def CustomTimetext(filetype, name):
    """ Timestamp, but in text form BUT with a custom filetype"""
    return f"{name}_{int(time.time())}.{filetype}"


def date(target, clock: bool = True, seconds: bool = False, ago: bool = False, only_ago: bool = False,
         raw: bool = False):
    if isinstance(target, int) or isinstance(target, float):
        target = datetime.utcfromtimestamp(target)

    if raw:
        if clock:
            timestamp = target.strftime("%d %B %Y, %H:%M")
        elif seconds:
            timestamp = target.strftime("%d %B %Y, %H:%M:%S")
        else:
            timestamp = target.strftime("%d %B %Y")

        if isinstance(target, int) or isinstance(target, float):
            target = datetime.utcfromtimestamp(target)
            target = calendar.timegm(target.timetuple())

        if ago:
            timestamp += f" ({timesince.format(target)})"
        if only_ago:
            timestamp = timesince.format(target)

        return f"{timestamp} (UTC)"
    else:
        unix = int(time.mktime(target.timetuple()))
        timestamp = f"<t:{unix}:{'f' if clock else 'D'}>"
        if ago:
            timestamp += f" (<t:{unix}:R>)"
        if only_ago:
            timestamp = f"<t:{unix}:R>"
        return timestamp


def responsible(target, reason):
    """ Default responsible maker targeted to find user in AuditLogs """
    responsible = f"[ {target} ]"
    if not reason:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case, mass=False):
    """ Default way to present action confirmation in chat """
    output = f"**{case}** the user"

    if mass:
        output = f"**{case}** the IDs/Users"

    return f"✅ Successfully {output}"


async def prettyResults(ctx, filename: str = "Results", resultmsg: str = "Here's the results:", loop=None):
    """ A prettier way to show loop results """
    if not loop:
        return await ctx.send("The result was empty...")

    pretty = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])

    if len(loop) < 15:
        return await ctx.send(f"{resultmsg}```ini\n{pretty}```")

    data = BytesIO(pretty.encode('utf-8'))
    await ctx.send(
        content=resultmsg,
        file=discord.File(data, filename=timetext(filename.title()))
    )


def naturalsize(size_in_bytes: int):
    """
    Converts a number of bytes to an appropriately-scaled unit
    E.g.:
        1024 -> 1.00 KiB
        12345678 -> 11.77 MiB
    """
    units = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')

    power = int(math.log(size_in_bytes, 1024))

    return f"{size_in_bytes / (1024 ** power):.2f} {units[power]}"


async def send(ctx, content=None, embed=None, ttl=None):
    perms = ctx.channel.permissions_for(ctx.me).embed_links
    ttl = None if ctx.message.content.endswith(' stay') else ttl
    try:
        if ttl and perms:
            await ctx.message.edit(content=content, embed=embed)
            await asyncio.sleep(ttl)
            try:
                await ctx.message.delete()
            except:
                log.error('Failed to delete Message in {}, #{}'.format(ctx.guild.name, ctx.channel.name))
                pass
        elif ttl is None and perms:
            await ctx.message.edit(content=content, embed=embed)
        elif embed is None:
            await ctx.message.edit(content=content, embed=embed)
        elif embed and not perms:
            await ctx.message.edit(content='\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds', delete_after=5)
    except:
        if embed and not perms:
            await ctx.message.edit(content='\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds', delete_after=5)
        else:
            await ctx.send(content=content, embed=embed, delete_after=ttl, file=None)
def renderBar(
    value: int,
    *,
    gap: int = 0,
    length: int = 32,
    point: str = "",
    fill: str = "-",
    empty: str = "-",
) -> str:
    # make the bar not wider than 32 even with gaps > 0
    length = int(length / int(gap + 1))

    # handles fill and empty's length
    fillLength = int(length * value / 100)
    emptyLength = length - fillLength

    # handles gaps
    gapFill = " " * gap if gap else ""

    return gapFill.join(
        [fill] * (fillLength - len(point)) + [point] + [empty] * emptyLength
    )