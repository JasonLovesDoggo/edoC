import asyncio
import io
import logging
import time
import json

import aiohttp
import discord
import traceback
import timeago as timesince
from io import BytesIO
from discord.ext import commands

from utils.data import MyNewHelp

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
        super().__init__(command_prefix="~", description=description,
                         pm_help=None, help_attrs=dict(hidden=True),
                         chunk_guilds_at_startup=False, heartbeat_timeout=150.0,
                         allowed_mentions=allowed_mentions, intents=intents,
                         owner_ids=confi["owners"], case_insensitive=True,
                         command_attrs=dict(hidden=True), help_command=MyNewHelp(), )
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.prefix = '~'
        #self.blacklist = Config('blacklist.json')
    #async def on_guild_join(self, guild):
    #    if guild.id in self.blacklist:
    #        await guild.leave()

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not can_handle(msg, "send_messages"):
            return

        await self.process_commands(msg)

class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def session(self):
        return self.bot.session

    async def safe_send(self, content, *, escape_mentions=True, **kwargs):
        """Same as send except with some safe guards.
        1) If the message is too long then it sends a file with the results instead.
        2) If ``escape_mentions`` is ``True`` then it escapes mentions.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            fp = io.BytesIO(content.encode())
            kwargs.pop('file', None)
            return await self.send(file=discord.File(fp, filename='message_too_long.txt'), **kwargs)
        else:
            return await self.send(content)


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
