import asyncio
import functools
import logging
import time
import json
from datetime import datetime

import discord
import traceback
import timeago as timesince
from io import BytesIO
from discord.ext import commands
from discord.ext.commands import NoPrivateMessage, when_mentioned_or

from utils.data import MyNewHelp
from utils.http import HTTPSession


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


def config(filename: str = "config"):
    """ Fetch default config file """
    try:
        with open(f"{filename}.json", encoding='utf8') as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


confi = config()
log = logging.getLogger(__name__)
description = 'Relatively simply awesome bot. Developed by Jake CEO of annoyance#1904'


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

    async def safe_send(self, content, *, escape_mentions=True, **kwargs):
        """Same as send except with some safe guards.
        1) If the message is too long then it sends a file with the results instead.
        2) If ``escape_mentions`` is ``True`` then it escapes mentions.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            fp = BytesIO(content.encode())
            kwargs.pop('file', None)
            return await self.send(file=discord.File(fp, filename='message_too_long.txt'), **kwargs)
        else:
            return await self.send(content)

class edoC(commands.AutoShardedBot):
    def __init__(self):
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
                         command_attrs=dict(hidden=True), help_command=MyNewHelp(), )
        self.session = HTTPSession(loop=self.loop)
        self.prefix = '~'
        # self.blacklist = Config('blacklist.json')

    # async def on_guild_join(self, guild):
    #    if guild.id in self.blacklist:
    #        await guild.leave()

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not can_handle(msg, "send_messages"):
            return

        await self.process_commands(msg)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()

    async def close(self):
        await super().close()
        await self.session.close()

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


def timeago(target):
    """ Timeago in easier way """
    return timesince.format(target)


def date(target, clock=True):
    """ Clock format using datetime.strftime() """
    if not clock:
        return target.strftime("%d %B %Y")
    return target.strftime("%d %B %Y, %H:%M")


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
