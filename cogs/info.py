import os
import pathlib
import platform
import time
from io import BytesIO
from typing import List, Tuple

import aiohttp
# from utils.transwrapper import google_translator
import googletrans
import humanize
import psutil
from discord.ext import commands
from discord.ext.commands import ColourConverter
from discord.ext.menus import ListPageSource
from googletrans import Translator
from pyshorteners import Shortener

from cogs.music import Paginator
from lib.db import db
from utils import default, permissions
from utils.gets import *
from utils.info import fetch_info
from utils.vars import *


class Menu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=3)

    async def write_page(self, fields=[]):
        embed = discord.Embed(title="Todo",
                              description="Welcome to the edoC Todo dialog!",
                              colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar.url)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed


# Hex to RGB
def hex_to_rgb(value):
    print(value)
    v = str(value)
    v = v.replace('#', '')
    lv = len(v)
    return tuple(int(v[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def convert_all_to_hex(inputcolor):
    pass


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.PADDING = 9
        self.process = psutil.Process(os.getpid())
        self.event = self.bot.get_cog("Events")
        self.oldcolorApiH = 'https://www.thecolorapi.com/id?hex='
        self.neweroldColorApi = 'https://api.color.pizza/v1/'
        self.colorApi = 'https://api.popcatdev.repl.co/color/'
        self.trans = googletrans.Translator()

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

    async def create_embed(self, description, field: List[Tuple] = None):
        embed_ = discord.Embed(description=description,
                               colour=orange)
        if field is not None:
            for name, value, inline in field:
                embed_.add_field(name=name, value=value, inline=inline)
        return embed_

    # @commands.command()
    # async def translate(self, ctx, *, message: commands.clean_content = None):
    #    """Translates a message to English using Google translate."""
    #
    #    loop = self.bot.loop
    #    if message is None:
    #        ref = ctx.message.reference
    #        if ref and isinstance(ref.resolved, discord.Message):
    #            message = ref.resolved.content
    #        else:
    #            return await ctx.send('Missing a message to translate')
    #
    #    #try:
    #    ret = await loop.run_in_executor(None, self.trans.translate, message)
    #    #except Exception as e:
    #    #    return await ctx.send(f'An error occurred: {e.__class__.__name__}: {e}')
    #
    #    embed = discord.Embed(title='Translated', colour=0x4284F3)
    #    src = googletrans.LANGUAGES.get(ret.src, '(auto-detected)').title()
    #    dest = googletrans.LANGUAGES.get(ret.dest, 'Unknown').title()
    #    embed.add_field(name=f'From {src}', value=ret.origin, inline=False)
    #    embed.add_field(name=f'To {dest}', value=ret.text, inline=False)
    #    await ctx.send(embed=embed)

    @commands.command()
    async def translate(self, ctx, *, text):
        translator = Translator()
        result = translator.translate(text)
        language = translator.detect(text)
        embed = discord.Embed(
            description=f"```css\nText: {text}\nTranslated: {result.text}\nLanguage: {language.lang}```",
            color=blue).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    # @commands.command(name='translate', aliases=['trans'])
    # async def translates(self, ctx, *, text):
    #    """``Translates a sentence into a specific language``"""
    #    #src, dest = languages.split('-')
    #    #trans = self.translator.translate(src=src, dest=dest, text=text)
    #    #embed = await self.create_embed(description='', field=[(text, f'`{trans.text}`', False)])
    #    #embed.set_footer(text=dest)
    #    #await ctx.send(embed=embed)
    #    translator = google_translator()
    #    translate_text = translator.translate('สวัสดีจีน', lang_tgt='en')
    #    await ctx.reply(translate_text)
    @commands.group()
    @commands.cooldown(rate=1, per=43200, type=commands.BucketType.user)
    async def report(self, ctx):
        """USAGE
        ```yaml
        ~report guild (reason)
        ~report user (reason)
        ~report bug (bug)
        ```"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @commands.command(brief="Shows the bot's uptime")
    async def uptime(self, ctx):
        """
        Shows the bot's uptime in days | hours | minutes | seconds
        """
        em = discord.Embed(
            description=f"{humanize.precisedelta(discord.utils.utcnow() - self.bot.start_time, format='%.0f')}",
            colour=0x2F3136,
        )
        em.set_author(name="Uptime")
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=em)
    @commands.command(aliases=['RC', 'Rcolor', 'RandColor'])
    async def RandomColor(self, ctx):
        random_number = random.randint(0, 16777215)
        hexhex = str(hex(random_number))
        hex_number = hexhex[2:]

        async with aiohttp.ClientSession() as cs:
            async with cs.get(self.colorApi + hex_number) as api:
                data = await api.json()
        embed = discord.Embed(color=int(hexhex, 0))
        embed.add_field(name='Name', value=data['name'], inline=False)
        embed.add_field(name='Hex Code', value=data['hex'], inline=False)
        embed.add_field(name='Rgb value', value=data['rgb'][3:], inline=False)
        embed.set_thumbnail(url=f'https://api.popcatdev.repl.co/color/image/{hex_number}?width=100&height=100')
        await ctx.send(embed=embed)

    @commands.command(aliases=['C', 'Colour'])
    async def Color(self, ctx, colorname: ColourConverter):
        """
        The following formats are accepted:

        ```html
        0x<hex>
        #<hex>
        0x#<hex>
        rgb(<number>, <number>, <number>)
        Any of the classmethod in Colour
        The _ in the name can be optionally replaced with spaces.
        Like CSS, <number> can be either 0-255 or 0-100% and <hex> can be either a 6 digit hex number or a 3 digit hex shortcut (e.g. #fff).
        ```
        """
        strcolor = str(colorname).replace('#', "")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(self.colorApi + strcolor) as api:
                data = await api.json()
        co = f'0x{strcolor}'
        embed = discord.Embed(color=int(co, 0))
        embed.add_field(name='Name', value=data['name'], inline=False)
        embed.add_field(name='Hex Code', value=data['hex'], inline=False)
        embed.add_field(name='Rgb value', value=data['rgb'][3:], inline=False)
        embed.set_thumbnail(url=f'https://api.popcatdev.repl.co/color/image/{strcolor}?width=100&height=100')
        await ctx.send(embed=embed)

    @Color.error
    async def Color_handler(self, ctx, error):
        """A local Error Handler for our command do_repeat.
        This will only listen for errors in Color.
        The global on_command_error will still be invoked after.
        """

        # Check if our required argument inp is missing.
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                description=f"Please do {ctx.prefix}help Color for more info",
                color=colors["error"]
            )
            embed.set_footer(text='(hint check the accepted formats)')
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
        file = open("todo.txt", "r")
        embeds = []
        if len(list(file)) <= 2000:
            return await ctx.reply(embed=discord.Embed(
                title="TodoPagination",
                color=blue,
                description=file.readlines()))
        i = 0

        while True:
            filelines = len(file.readlines())
            if len(list(file)) - i > 200:
                embeds.append(discord.Embed(
                    title="TodoPagination",
                    description=list(file)[i:i + 1999],
                    color=blue))
            elif len(list(file)) - i <= 0:
                break
            else:
                embeds.append(discord.Embed(
                    title="TodoPagination",
                    description=list(file)[i:len(list(file)) - 1],
                    color=blue))
                break
            i += 1999

        return await ctx.reply(embed=embeds[0], view=Paginator(ctx=ctx, embeds=embeds))

    @commands.command(aliases=['len'])
    async def length(self, ctx, *, word):
        await ctx.reply(len(word))

    @commands.command(aliases=["URLshorten"])
    async def shorten(self, ctx, *, url):
        s = Shortener()
        ShortenedUrl = s.owly.short(url)
        await ctx.reply(embed=discord.Embed(description=ShortenedUrl, colour=random_color()))

    @commands.command(aliases=["URLexpand"])
    async def expand(self, ctx, *, url):
        s = Shortener()
        ExpandedUrl = s.owly.expand(url)
        await ctx.reply(embed=discord.Embed(description=ExpandedUrl, colour=random_color))

    # @commands.command()
    # async def time(self, ctx):
    #    """ Check what the time is for me (the bot) """
    #    time = datetime.utcnow().strftime("%d %B %Y, %H:%M")
    #    await ctx.send(f"Currently the time for me is **{time}**")

    # ~~~~~~~~~~~~~~~~~~~~~~~~
    @commands.command()
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.guild)
    async def CmdStats(self, ctx):
        cmdsran = self.bot.commands_ran
        marklist = sorted(cmdsran.items(), key=lambda x: x[1], reverse=True)
        sortdict = dict(marklist)
        p = ctx.prefix
        value_iterator = iter(sortdict.values())
        key_iterator = iter(sortdict.keys())
        emby = discord.Embed(title='edoC command Stats',
                             description=f'{self.bot.total_commands_ran} Commands ran this boot\n',
                             color=random_color())

        emby.add_field(name='Top 10 commands ran', value=f'🥇:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🥈:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🥉:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                                         f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n')

        emby.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        await ctx.reply(embed=emby)

    @commands.command(aliases=["stats", "status", "botinfo", "in"])
    async def about(self, ctx):
        proc = psutil.Process()
        infos = fetch_info()

        with proc.oneshot():
            mem = proc.memory_full_info()

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
            cmds = self.bot.total_commands_ran
            uptime = humanize.naturaldelta(discord.utils.utcnow() - self.bot.start_time)
            e.add_field(
                name="__:gear: Usage__",
                value=
                f"**{pmem}** physical memory\n"
                f"**{vmem}** virtual memory\n"
                f"**{uptime}** Uptime\n"
                f"**{cmds}** Commands ran this boot\n",
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
    @commands.has_permissions(attach_files=True)
    async def sendasfile(self, ctx, *, text: str):
        """ sends whatever the user sent as a file"""
        data = BytesIO(text.encode("utf-8"))
        await ctx.reply(file=discord.File(data, filename=f"{default.timetext('Text')}"))

    @commands.command(aliases=["SAFF"])
    @commands.has_permissions(attach_files=True)
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
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)
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

    def top10(self):
        for key, v in self.items():
            return key


def setup(bot):
    bot.add_cog(Info(bot))
