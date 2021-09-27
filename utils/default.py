# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import functools
import json
import logging
import math
import time
import traceback
from asyncio import sleep
from calendar import calendar
from datetime import datetime
from distutils.log import info
from glob import glob
from importlib import import_module
from io import BytesIO
from os import getpid, remove

import alexflipnote
import apscheduler.schedulers.asyncio
import discord
import timeago as timesince
from discord.ext import commands, tasks
from discord.ext.commands import NoPrivateMessage
from discord.utils import utcnow
from psutil import Process

# from lib.db import db
from utils import sqlite
from utils.Context import edoCContext
from utils.apis.Somerandomapi import SRA
from utils.cache import CacheManager
from utils.help import PaginatedHelpCommand
from utils.http import HTTPSession
from utils.vars import dark_blue, invis

BannedUsers = {}
logger = logging.getLogger(__name__)


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


class BaseEmbed(discord.Embed):
    def __init__(self, color=invis, fields=(), field_inline=False, **kwargs):
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


class edoC(commands.AutoShardedBot):
    def __init__(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.now()
        self.config = config()
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
            presences=True,
        )
        super().__init__(command_prefix=self.get_prefix, description=description,
                         pm_help=None, help_attrs=dict(hidden=True),
                         chunk_guilds_at_startup=False, heartbeat_timeout=150.0,
                         allowed_mentions=allowed_mentions, intents=intents,
                         owner_ids=confi["owners"], case_insensitive=True,
                         command_attrs=dict(hidden=True), help_command=PaginatedHelpCommand(),
                         activity=discord.Game(
                             type=discord.ActivityType.listening,
                             name=f"Listening to over {self.get_data('MemberCount')} Members spread over {self.get_data('GuildCount')} Guilds!\nPrefix: ~"
                         ), status=discord.Status.idle, )

        self.session = HTTPSession(loop=self.loop)
        self.prefix = '~'
        self.process = Process(getpid())
        self.tempimgpath = 'data/img/temp/*'
        self.ownerid = 511724576674414600
        self.icons = {}
        self.commands_ran = {}
        self.ready = False
        self.loading_status = {}
        self.sra = SRA(session=self.session)
        import os
        for root, dirs, files in os.walk("utils"):
            for f in files:
                if f.endswith('.py'):
                    import_module(str(os.path.relpath(os.path.join(root, f), "."))[:-3].replace('\\', '.'))
        self.db = sqlite.Database()
        if not self.create_drop_tables("create"):
            print('hi')
        self.seen_messages = 0
        self.scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()
        self.total_commands_ran = 0
        self.alex_api = alexflipnote.Client(confi['alexflipnote_api'],
                                            loop=self.loop)  # just a example, the client doesn't have to be under bot and loop kwarg is optional
        self.cache = CacheManager()
        self.prefixs = {}

        # self.blacklist = Config('blacklist.json')

    # async def on_guild_join(self, guild):
    #    if guild.id in self.blacklist:
    #        await guild.leave()

    def create_drop_tables(self, method: str):
        all_tables = [g for g in sqlite.Table.all_tables()]
        for table in all_tables:
            try:
                getattr(table, method)()
            except Exception as e:
                print(f'Could not {method} {table.__tablename__}.\n\nError: {e}')
            else:
                print(f'[{table.__module__}] {method}ed {table.__tablename__}.')
        return all_tables

    def backup_data(self):
        self.save_data('MsgsSeen', str(self.seen_messages))
        self.save_data('MemberCount', str(sum(g.member_count for g in self.guilds)))
        self.save_data('GuildCount', str(len(self.guilds)))

    def save_data(self, endpoint: str, changeto: str):
        """ Temp db system """
        db_name = 'C:\\Users\\Jason\\edoC\\tempdb.json'
        with open(db_name, "r") as jsonFile:
            data = json.load(jsonFile)
        data[endpoint] = changeto
        with open(db_name, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2)
        jsonFile.close()

    def get_data(self, endpoint):
        """ Temp db system """
        try:
            with open('C:\\Users\\Jason\\edoC\\tempdb.json', 'r', encoding='utf8') as data:
                jsondata = json.load(data)
                return jsondata[endpoint]
        except FileNotFoundError:
            raise FileNotFoundError("JSON file wasn't found")

    @tasks.loop(seconds=25)
    async def update_data(self):
        self.backup_data()

    async def load_prefixs(self):
        await self.wait_until_ready()
        print('loading prefixs')
        for guild in self.guilds:
            data = self.db.fetch('SELECT prefix FROM prefixs WHERE id = ?', (guild.id,))
            for dic in data:
                for prefix in dic.values():
                    self.prefixs[guild.id] = prefix
        self.loading_status['Prefixs'] = True

    async def update_db(self):
        print('starting to update db this might take a bit')
        for guild in self.guilds:
            self.db.execute("INSERT OR IGNORE INTO guilds (id) VALUES (?)",
                            (guild.id,))
            self.db.execute('INSERT OR IGNORE INTO prefixs (id, author, timestamp) VALUES (?, ?, ?)',
                            (guild.id, self.user.id, time.time(),))
        to_remove = []
        allmembers = self.get_all_members()
        for user in allmembers:
            if user.bot:
                continue
            self.db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)",
                            (user.id,))
        stored_members = self.db.fetch("SELECT id FROM users")
        for member in stored_members:
            id_ = member['id']
            #print(id_)
            if id_ not in allmembers:
                print(f'id_ = {id_}, member = {member}')
                to_remove.append(id_)

        #print(to_remove)
        # for id in to_remove:
        #    print(f'deleting {id} from users')
        #    self.db.execute("DELETE FROM users WHERE id = ?", (id,))

        print("updated db")

    async def get_prefix(self, msg):
        guild = msg.guild
        user_id = self.user.id
        base = [f'<@!{user_id}> ', f'<@{user_id}> ']
        if guild is None:
            base.append(self.prefix)
        else:
            if guild.id in self.prefixs.keys():
                base.extend(self.prefixs.get(guild.id, [self.prefix]))
            else:
                self.db.execute("INSERT OR IGNORE INTO prefixs (id) VALUES (?)",
                                (guild.id,))
                self.prefixs[guild.id] = self.db.fetch('SELECT prefix FROM prefixs WHERE id = ?', (guild.id,))
                base.extend(self.prefixs.get(guild.id, [self.prefix]))
        return base
        # if guild is None:
        #    return self.prefix
        # elif guild.id in self.prefixs.keys():
        #    print(self.prefixs[guild.id])
        #    return self.prefixs[guild.id]
        # else:
        #    self.db.execute("INSERT OR IGNORE INTO prefixs (id) VALUES (?)",
        #                    (guild.id,))
        #    self.prefixs[guild.id] = when_mentioned_or(self.db.fetch('SELECT prefix FROM prefixs WHERE id = ?', (guild.id,)))

    async def get_url(self, url) -> dict:
        async with self.session.get(url) as ses:
            data = await ses.json()
        return data

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not can_handle(msg, "send_messages"):
            return
        self.seen_messages += 1
        if bool(msg.raw_mentions):
            if msg.raw_mentions[0] == 845186772698923029 and len(msg.content) == 22:
                context = await self.get_context(msg, cls=edoCContext)
                await context.send_help()
        ctx = await self.get_context(msg)
        is_command = ctx.valid
        if is_command:
            check = await self.get_guild_permissions(ctx)
            if not check:
                return await self.send_missing_perms(ctx)
            await self.process_commands(msg)

    async def exit(self, code):
        await sleep(3)
        exit(code)

    async def close(self) -> None:
        self.update_data.stop()
        self.backup_data()
        await self.session.close()
        await self.exit(600)
        await super().close()

    async def restart(self) -> None:
        self.update_data.stop()
        self.backup_data()
        await self.exit(601)
        await self.session.close()
        await super().close()

    def loading_emojis(self):
        emojis = {
            "greenTick": "<a:yes:879161309315346582>",
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
            'database': '<:database:889257927762919424>',
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

    async def get_context(self, message, *, cls=edoCContext) -> edoCContext:
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        """ The function that activates when boot was completed """
        logschannel = self.get_channel(self.config["edoc_non_critical_logs"])
        await self.update_db()
        await self.load_prefixs()
        if not self.ready:
            for command in self.walk_commands():
                self.commands_ran[f'{command.qualified_name}'] = 0
            self.seen_messages = int(self.get_data('MsgsSeen'))
            await emptyfolder(self.tempimgpath)
            self.update_data.start()
            self.ready = True
            self.scheduler.start()
            await logschannel.send(f"{self.user} has been booted up")
            # Indicate that the bot has successfully booted up
            print(
                f"Ready: {self.user} | Total members {sum(g.member_count for g in self.guilds)} | Guild count: {len(self.guilds)} | Guilds")
            guilds = {}
            for Server in self.guilds:
                gprefix = self.prefixs[Server.id]
                print(
                    f"{Server.id} ~ {Server} ~ {Server.owner} ~ {Server.member_count} ~ Prefix {gprefix}")
            self.loading_emojis()
            await self.fill_cache()
        else:
            print(f"{self.user} Reconnected")
            await logschannel.send(f"{self.user} has been reconnected")

    def bool_to_emoji(self, boo: bool):
        if boo:
            return self.icons['greenTick']
        else:
            return self.icons['redTick']

    async def get_guild_permissions(self, ctx, return_dict=False):
        all_perms = {}
        admin = ctx.guild.me.guild_permissions.administrator
        all_perms['Add Reactions'] = ctx.guild.me.guild_permissions.add_reactions
        all_perms['View Audit Log'] = ctx.guild.me.guild_permissions.view_audit_log
        all_perms['Read Messages'] = ctx.guild.me.guild_permissions.read_messages
        all_perms['Send Messages'] = ctx.guild.me.guild_permissions.send_messages
        all_perms['Embed Links'] = ctx.guild.me.guild_permissions.embed_links
        all_perms['Attach Files'] = ctx.guild.me.guild_permissions.attach_files
        all_perms['read Message History'] = ctx.guild.me.guild_permissions.read_message_history
        all_perms['External Emojis'] = ctx.guild.me.guild_permissions.external_emojis
        all_perms['Connect'] = ctx.guild.me.guild_permissions.connect
        all_perms['Speak'] = ctx.guild.me.guild_permissions.speak

        # stealemoji cmd only manage_emojis = ctx.guild.me.guild_permissions.manage_emojis
        # needed for mod perms x = ctx.guild.me.guild_permissions.manage_roles
        if return_dict:
            return all_perms
        if all(all_perms.values()):
            return True
        return False

    async def send_missing_perms(self, ctx):
        perms = await self.get_guild_permissions(ctx, return_dict=True)
        emb = discord.Embed(color=invis, description='', title='Missing permissions!')
        for name, perm in perms.items():
            emb.description += f'{self.bool_to_emoji(perm)} {name}\n'
        try:
            return await ctx.send(embed=emb)
        except discord.Forbidden:
            to_send = 'Missing Permissions!\n'

            for name, perm in perms.items():
                to_send += f'{self.bool_to_emoji(perm) if perms["External Emojis"] else perm} {name}\n'
            return await ctx.send(to_send)

    async def on_command(self, ctx):
        try:
            self.commands_ran[ctx.command.qualified_name] += 1
        except KeyError:
            pass
        self.total_commands_ran += 1
        # if ctx.author.id in BannedUsers:
        #    return
        # else:
        #    blocked = False
        try:
            try:
                try:
                    print(
                        f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content} ")  # > Blocked {blocked}")
                    info(f'{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}')
                except AttributeError:
                    print(f"Private message > {ctx.author} > {ctx.message.clean_content}")  # > Blocked {blocked}")
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
        # query = 'SELECT * FROM (SELECT guild_id AS snowflake_id, blacklisted  FROM guild_config  UNION ALL SELECT user_id AS snowflake_id, blacklisted  FROM users_data) WHERE blacklisted="TRUE"'
        # cur = await self.db.execute(query)
        # data = await cur.fetchall()
        # self.cache["blacklisted_users"] = {r[0] for r in data} or set()
        #
        # """Loading up premium users."""
        # query = 'SELECT * FROM (SELECT guild_id AS snowflake_id, premium  FROM guild_config  UNION ALL SELECT user_id AS snowflake_id, premium  FROM users_data) WHERE premium="TRUE"'
        # cur = await self.db.execute(query)
        # data = await cur.fetchall()
        # self.cache["premium_users"] = {r[0] for r in data} or set()
        #
        # """Loading up users that have tips enabled"""
        # query = 'SELECT user_id FROM users_data WHERE tips = "TRUE"'
        # cur = await self.db.execute(query)
        # data = await cur.fetchall()
        # self.cache["tips_are_on"] = {r[0] for r in data} or set()
        #
        # """Loading up users that have mentions enabled"""
        # query = 'SELECT user_id FROM users_data WHERE mentions = "TRUE"'
        # cur = await self.db.execute(query)
        # data = await cur.fetchall()
        # self.cache["mentions_are_on"] = {r[0] for r in data} or set()
        #
        # """Loads up all disabled_commands"""
        # query = "SELECT command_name, snowflake_id FROM disabled_commands ORDER BY command_name"
        # cur = await self.db.execute(query)
        # data = await cur.fetchall()
        # self.cache["disabled_commands"] = {
        #    cmd: [r[1] for r in _group]
        #    for cmd, _group in itertools.groupby(data, key=operator.itemgetter(0))
        # }

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
