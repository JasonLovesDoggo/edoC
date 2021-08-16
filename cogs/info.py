import os
import platform
import time
from io import BytesIO

import aiohttp
import humanize
import psutil
from discord.ext.menus import ListPageSource, MenuPages
from pyshorteners import Shortener
import discord
from discord.ext import commands
from utils.info import fetch_info
from utils.vars import *
from utils import default, permissions
from lib.db import db
import pathlib
from utils.gets import *
from PIL import Image


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


# Hex to RGB
def hex_to_rgb(value):
    value = value.replace('#', '')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def convert_all_to_hex(inputcolor):
    pass


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.PADDING = 9
        self.process = psutil.Process(os.getpid())
        self.event = self.bot.get_cog("Events")
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.utcnow()
        self.oldcolorApiH = 'https://www.thecolorapi.com/id?hex='
        self.ColorApi = 'https://api.color.pizza/v1/'

        # @commands.command(aliases=["UIS", "UsersSpotify"])
        # async def UserInfoSpotify(ctx, user: discord.Member = None):
        #    if not user:
        #        user = ctx.author
        #        pass
        #    if user.activities:
        #        for activity in user.activities:
        #            from discord import Spotify
        #            if isinstance(activity, Spotify):
        #                embed = discord.Embed(
        #                    title=f"{user.name}'s Spotify",
        #                    description="Listening to {}".format(activity.title),
        #                    color=green)
        #                embed.set_thumbnail(url=activity.album_cover_url)
        #                embed.add_field(name="Artist", value=activity.artist)
        #                embed.add_field(name="Album", value=activity.album)
        #                embed.set_footer(text="Song started at {}".format(activity.created_at.strftime("%H:%M")))
        #                await ctx.send(embed=embed)

    # @commands.group()
    # async def color(self, ctx, colorC):
    #    """ blank """
    #    if ctx.invoked_subcommand is None:
    #        basecolor = str(Color(colorC).hex).replace('#', '')
    #        im = Image.new("RGB", (100, 100), colorC)
    #        im.
    #        #img = discord.File(fp=im, filename=f'{basecolor}.png')
    #        Cemb = discord.Embed(title=colorC, color=red)
    #        Cemb.set_image(url=im)
    #        await ctx.send(embed=Cemb)

    # @color.command()
    # async def help(self, ctx):
    #    await ctx.reply("Please use ~help color")

    # @color.command()
    # async def list(self, ctx):
    #    await ctx.send(f"```py\n{ValidDefColors}\n```")

    """        async with aiohttp.ClientSession() as cs:
            async with cs.get(self.colorApiH + color) as api:
                data = await api.json()
        if color is None:
            role = getRole(ctx, color)
            if role:
                color = getColor(str(role.color))
        if color:
            value = Color(color).hex_l.strip('#')

            e = discord.Embed(title=Color(color).web.title(), colour=int(value, 16))
            e.url = f'http://www.colorhexa.com/{value}'
            e.add_field(name='HEX', value=Color(color).hex_l)
            e.add_field(name='RGB', value=Color(color).rgb)
            e.add_field(name='HSL', value=Color(color).hsl)
            e.set_image(url=f'http://www.colorhexa.com/{value}.png')
            await send(ctx, embed=e)
        else:
            await send(ctx, '\N{HEAVY EXCLAMATION MARK SYMBOL} Could not find color', ttl=3)
        await ctx.reply(data['hex'])"""

    @commands.command(aliases=['CColour', 'CC'])
    async def Ccolor(self, ctx, colorname: str):
        """Convert Color from HEX to RGB or simply search for webcolors."""
        colorname.replace('#', '')
        async with aiohttp.ClientSession() as cs:
            async with cs.get(self.ColorApi + colorname) as api:
                data = await api.json()
                data = data['colors'][0]
        await ctx.send(self.ColorApi + colorname)
        await ctx.reply(data)
        cdata = data['rgb']
        r = cdata['r']
        g = cdata['g']
        b = cdata['b']
        img = Image.new('RGB', (300, 250), (r, g, b))
        img.save(fp=f'data/img/temp/{ctx.message.id}.png')
        embed = discord.Embed(color=discord.Color.from_rgb(r=r, g=g, b=b), title=data['name'])
        embed.set_footer(text=f"Distance from color {str(round(data['distance'], ndigits=2))}")
        embed.set_image(url=f"attachment://data/img/temp/{ctx.message.id}.png")
        await ctx.send(embed=embed)

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

    @commands.command(aliases=['len'])
    async def length(self, ctx, *, word):
        await ctx.reply(len(word))

    @commands.command(aliases=["URLshorten"])
    async def shorten(self, ctx, *, url):
        s = Shortener()
        ShortenedUrl = s.owly.short(url)
        await ctx.reply(embed=discord.Embed(description=ShortenedUrl, colour=random_color))

    @commands.command(aliases=["URLexpand"])
    async def expand(self, ctx, *, url):
        s = Shortener()
        ExpandedUrl = s.owly.expand(url)
        await ctx.reply(embed=discord.Embed(description=ExpandedUrl, colour=random_color))

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
                value=version_info["info"].title(),
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
        await ctx.reply(file=discord.File(data, filename=f"{default.CustomTimetext(filetype, 'Text')}"))

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
            elif str(f).startswith("node_modules"):
                continue
            elif str(f).startswith("ffmpeg"):
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
