import os
import platform
import random
import time
from io import BytesIO

import humanize
import psutil
from discord.ext.menus import ListPageSource, MenuPages

import discord
from datetime import datetime
from discord.ext import commands

from utils.info import fetch_info
from utils.vars import *
from utils import default, permissions
from lib.db import db
import pathlib

class Menu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=3)

    async def write_page(self, fields=[]):

        embed = discord.Embed(title="Todo",
                              description="Welcome to the edoC Todo dialog!",
                              colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.PADDING = 9
        self.process = psutil.Process(os.getpid())
        self.event = self.bot.get_cog("Events")
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.utcnow()

    async def todomenu(self, ctx, command):
        embed = discord.Embed(title=f"TODO",
                              description="test",
                              colour=ctx.author.colour)
        embed.add_field(name="Command description", value=command.help)
        await ctx.send(embed=embed)

    @commands.command(aliases=["todomenu"])
    async def todo(self, ctx):
        """Shows this message."""
        file = open("todo.txt", "r").readlines()
        menu = MenuPages(source=Menu(ctx, list(file)),
                         delete_message_after=True,
                         timeout=60.0)
        await menu.start(ctx)

    @commands.command()
    async def time(self, ctx):
        """ Check what the time is for me (the bot) """
        time = datetime.utcnow().strftime("%d %B %Y, %H:%M")
        await ctx.send(f"Currently the time for me is **{time}**")

    # ~~~~~~~~~~~~~~~~~~~~~~~~
    @commands.command(aliases=["about", "stats", "status", "botinfo", "in"])
    async def info(self, ctx):
        proc = psutil.Process()
        infos = fetch_info()

        with proc.oneshot():
            mem = proc.memory_full_info()
            cpu = proc.cpu_percent() / psutil.cpu_count()

            e = discord.Embed(
                title="Information about edoC",
                color=0x89C4F9,
            )

            e.add_field(
                name=(
                    "__:busts_in_silhouette: Development__"
                ),
                value="**Jake CEO of annoyance#1904:** [GitHub](https://github.com/JakeWasChosen)\n",
                inline=True,
            )
            e.add_field(
                name="__<:python:868285625877557379> Python__",
                value=f"**python** `{platform.python_version()}`\n"
                      f"**discord.py** `{discord.__version__}`",
                inline=True,
            )

            pmem = humanize.naturalsize(mem.rss)
            vmem = humanize.naturalsize(mem.vms)

            e.add_field(
                name="__:gear: Usage__",
                value=
                f"**{pmem}** physical memory\n"
                f"**{vmem}** virtual memory\n"
                f"**{cpu:.2f}**% CPU",
                inline=True)

            e.add_field(
                name="__Servers count__",
                value=str(len(self.bot.guilds)),
                inline=True,
            )
            e.add_field(
                name="__Channels count__",
                value=str(len(list(self.bot.get_all_channels()))),
                inline=True,
            )
            e.add_field(
                name="__Members count__",
                value=str(len(list(self.bot.get_all_members()))),
                inline=True,
            )

            e.add_field(
                name="__:file_folder: Files__",
                value=f"{infos.get('file_amount')} "
                      f"*({infos.get('python_file_amount')}"
                      f" <:python:868285625877557379>)*",
                inline=True,
            )
            e.add_field(  # (class, functions, coroutines, comments)
                name="__¶ Lines__",
                value=f"{infos.get('total_lines')} "
                      f" *({infos.get('total_python_class')} class"
                      + ","
                        f" {infos.get('total_python_functions')} functions"
                      + ","
                        f" {infos.get('total_python_coroutines')} coroutines"
                      + ","
                        f" {infos.get('total_python_comments')} comments"
                      + ")*",
                inline=True,
            )

            e.add_field(
                name="__Latest changes__",
                value=version_info["info"],
                inline=False,
            )

            e.add_field(
                name="__:link: Links__",
                value="[edoC](https://dsc.gg/edoc) "
                      "| [dev links](https://bio.link/edoC) "
                      "| [support me](https://www.buymeacoffee.com/edoC) "
                      "| [invite](https://discordapp.com/oauth2/authorize?client_id=845186772698923029&scope=bot&permissions=8) ",
                inline=False,
            )
            prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?",
                              ctx.guild.id)
            e.set_footer(
                text=f"version: {version_info['version']} • prefix: {prefix} • {len([x.name for x in self.bot.commands])} commands loaded\n {embedfooter}")

        await ctx.send(embed=e)

    # ~~~
    @commands.command(aliases=["SAF"])
    @permissions.has_permissions(attach_files=True)
    async def sendasfile(self, ctx, *, text: str):
        """ sends whatever the user sent as a file"""
        data = BytesIO(text.encode("utf-8"))
        await ctx.reply(file=discord.File(data, filename=f"{default.timetext('Text')}"))

    @commands.command(aliases=["SAFF"])
    @permissions.has_permissions(attach_files=True)
    async def sendasformatedfile(self, ctx, filetype: str, *, text: str):
        """ sends whatever the user sent as a file BUT with a specified filetype"""
        data = BytesIO(text.encode("utf-8"))
        await ctx.reply(file=discord.File(data, filename=f"{default.CustomTimetext(filetype ,'Text')}"))

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command()
    async def lines(self, ctx):
        """ gets all lines"""
        global color
        p = pathlib.Path('./')
        cm = cr = fn = cl = ls = fc = 0
        for f in p.rglob('*.py'):
            if str(f).startswith("venv"):
                continue
            fc += 1
            with open(f, 'rb') as of:
                for l in of.read().decode().splitlines():
                    l = l.strip()
                    if l.startswith('class'):
                        cl += 1
                    if l.startswith('def'):
                        fn += 1
                    if l.startswith('async def'):
                        cr += 1
                    if '#' in l:
                        cm += 1
                    ls += 1
        lang = random.choice(["ahk", "apache", "prolog"])
        if lang == "apache":
            color = orange
        elif lang == "ahk":
            color = blue
        elif lang == "prolog":
            color = 0x7e2225
        e = discord.Embed(title="Lines",
                          color=color,
                          timestamp=ctx.message.created_at)
        e.description = f"```{lang}\nFiles: {fc}\nLines: {ls:,}\nClasses: {cl}\nFunctions: {fn}\nCoroutines: {cr}\nComments: {cm:,}\n ```"
        e.set_footer(text=f"Requested by {ctx.author.name}\n{embedfooter}")
        await ctx.send(embed=e)

    @commands.command(aliases=["joinme", "inviteme", "botinvite"])
    async def invite(self, ctx):
        """Sends you the bot invite link."""
        perms = discord.Permissions.none()
        perms.administrator = True
        await ctx.reply(
            f"**{ctx.author.name}**, use this URL to invite me\n<{discord.utils.oauth_url(self.bot.user.id, perms)}>")

    @commands.command()
    async def changehelp(self, ctx):
        """ Give Info on ~change """
        await ctx.reply("""~change 
                        Commands:
                        avatar   Change avatar. 
                        nickname Change nickname. 
                        playing  Change playing status. 
                        username Change username. 

                        Type ~help command for more info on a command.
                        You can also type ~help category for more info on a category.""")

    @commands.command(aliases=["code"])
    async def source(self, ctx):
        """ Check out my source code <3 """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT.
        await ctx.reply(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/JakeWasChosen/edoC")

    @commands.command(aliases=["supportserver", "feedbackserver"])
    async def botserver(self, ctx):
        """ Get an invite to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 819282410213605406:
            return await ctx.send(f"**Here you go {ctx.author.name} 🍻\n<{self.config['botserver']}>**")
        await ctx.reply(f"**{ctx.author.name}** this is my home you know :3")

    @commands.command(hidden=True)
    async def altinfo(self, ctx):
        """ About the bot """

        ramUsage = self.process.memory_full_info().rss / 1024 ** 2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)
        totalmembers = sum(g.member_count for g in self.bot.guilds)
        embed = discord.Embed(colour=green)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Last boot", value=default.timeago(datetime.now() - self.bot.uptime), inline=True)
        embed.add_field(
            name=f"Developer (bio)[https://bio.link/edoc]",
            value=", ".join([str(self.bot.get_user(x)) for x in self.config["owners"]]),
            inline=True
        )
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Total Members", value=totalmembers)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )",
                        inline=True)
        embed.add_field(name="Commands Loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="Commands Ran By Owners", value=None)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)
        embed.set_footer(text=embedfooter)
        await ctx.send(content=f"ℹ About **{ctx.bot.user}** | **{version_info['version']}**", embed=embed)

    @commands.command(aliases=["bs"])
    async def botstats(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024 ** 2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)
        totalmembers = sum(g.member_count for g in self.bot.guilds)
        em = discord.Embed(title="WIP stats design",
                           colour=dark_blue,
                           timestamp=ctx.message.created_at,
                           description="")
        info = {}
        info["Discord.py version"] = discord.__version__
        info["Python Version"] = f"{platform.python_version()}"
        info["Avg users/server"] = f"{avgmembers:,.2f}"
        info["commands ran since restart"] = self.event.normal_commands
        info["Commands ran by owners"] = self.event.owner_commands
        info["Bot owners"] = len(self.config["owners"])
        info["Prefix in this server"] = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?",
                                                 ctx.guild.id)  # get_prefix(self.bot, ctx)
        info["Total members"] = totalmembers
        info["Ram usage"] = f"{ramUsage:.2f} MB"
        info["Developer"] = "Jake CEO of annoyance#1904"

        for k, v in info.items():
            pad = ' ' * (self.PADDING - len(str(v)))
            em.description += f"`{pad}{v}`: **{k}**\n"
        em.set_footer(text="bot owners are excluded from command stats")
        await ctx.send(content=f"About **{ctx.bot.user}** | **{version_info['version']}**", embed=em)
        await ctx.send("||https://bio.link/edoC||")

    @commands.command()
    async def developer(self, ctx):
        emb = discord.Embed(title="Jason",
                            color=blue,
                            timestamp=ctx.message.created_at
                            )
        devinfo = {}
        devinfo["yes"] = "no"
        for k, v in devinfo.items():
            pad = ' ' * (self.PADDING - len(str(v)))
            emb.description += f"`{pad}{v}`: **{k}**\n"

        emb.set_footer(text="Please consider donating")

    @commands.guild_only()
    @commands.command()
    async def emote(self, ctx, msg: str = None):
        """List all emotes in this server."""
        if msg:
            server, found = ctx.find_server(msg)
            if not found:
                return await ctx.send(server)
        else:
            server = ctx.message.server
        emojis = [str(x) for x in server.emojis]
        await ctx.say(" ".join(emojis))


def setup(bot):
    bot.add_cog(Information(bot))
