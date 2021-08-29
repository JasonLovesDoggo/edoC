# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from pathlib import Path
from platform import python_version, system
from typing import List, Tuple

from discord import HTTPException
from discord.ext.commands import ColourConverter
from discord.ext.menus import ListPageSource
from googletrans import Translator
from humanize import precisedelta
from pyshorteners import Shortener

from utils.default import *
from utils.info import fetch_info
from utils.pagination import Paginator
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


class Info(commands.Cog, description='Informational and useful commands'):
    def __init__(self, bot):
        self.bot = bot
        self.config = config()
        self.PADDING = 9
        self.process = self.bot.process
        self.event = self.bot.get_cog("Events")
        self.oldcolorApiH = 'https://www.thecolorapi.com/id?hex='
        self.neweroldColorApi = 'https://api.color.pizza/v1/'
        self.colorApi = 'https://api.popcatdev.repl.co/color/'
        self.trans = Translator()
        self.logs = self.bot.get_channel(self.config["edoc_logs"])

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

    async def create_embed(self, description, field: List[Tuple] = None):
        embed_ = discord.Embed(description=description,
                               colour=orange)
        if field is not None:
            for name, value, inline in field:
                embed_.add_field(name=name, value=value, inline=inline)
        return embed_

    @commands.command(aliases=['trans'])
    async def translate(self, ctx, *, message: commands.clean_content = None):
        """Translates a message to English using Google translate."""

        loop = self.bot.loop
        if message is None:
            ref = ctx.message.reference
            if ref and isinstance(ref.resolved, discord.Message):
                message = ref.resolved.content
            else:
                return await ctx.reply(embed=discord.Embed(description='Missing a message to translate', color=error))

        try:
            ret = await loop.run_in_executor(None, self.trans.translate, message)
        except Exception as e:
            return await ctx.send(f'An error occurred: {e.__class__.__name__}: {e}')

        embed = discord.Embed(colour=blue)
        src = LANGUAGES.get(ret.src, '(auto-detected)').title()
        dest = LANGUAGES.get(ret.dest, 'Unknown').title()
        embed.set_author(name='Translated', icon_url='https://i.imgur.com/kqYmKR6.png')
        embed.add_field(name=f'From {src}', value=ret.origin, inline=False)
        embed.add_field(name=f'To {dest}', value=ret.text, inline=False)
        try:
            await ctx.reply(embed=embed)
        except HTTPException:
            await ctx.reply('msg too long')

    @commands.group()
    @commands.cooldown(rate=1, per=43200, type=commands.BucketType.user)
    async def report(self, ctx):
        """USAGE
        ```yaml
        ~report guild (reason) < DOESNT EXIST RN
        ~report user (user) (reason)
        ~report bug (bug-other details)~ < DOESNT EXIST RN
        ```
        If you abuse this command you will get blacklisted
        **No chance for appeal**"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @report.command()
    async def user(self, ctx, user: discord.Member, *, reason: str = None):
        channel = self.logs
        author = ctx.message.author
        await ctx.message.delete()  # Privacy on the users part
        if not reason:
            await author.send('You must provide a reasoning to report a user/guild')
        elif len(reason) > 1900:
            return await author.send('Your Reason must be under 1900 characters')
        else:
            await channel.send(embed=ReportEmbed(ctx=ctx, type='Member', body=reason, directed_at=user))
            # await channel.send(f"{author} has reported {user}, reason: {reason}")

    @commands.command(brief="Shows the bot's uptime")
    async def uptime(self, ctx):
        """
        Shows the bot's uptime in days | hours | minutes | seconds
        """
        em = discord.Embed(
            description=f"{precisedelta(discord.utils.utcnow() - self.bot.start_time, format='%.0f')}",
            colour=0x2F3136,
        )
        em.set_author(name="Uptime")
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=em)

    @commands.command(aliases=['RC', 'Rcolor', 'RandColor'])
    async def RandomColor(self, ctx):
        random_number = random.randint(0, 16777215)
        hexhex = str(hex(random_number))
        hex_number = hexhex[2:]

        async with self.bot.session.get(self.colorApi + hex_number) as api:
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
        async with self.bot.session.get(self.colorApi + strcolor) as api:
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
    # @commands.cooldown(rate=1, per=300, type=commands.BucketType.guild)
    async def CmdStats(self, ctx):
        try:
            cmdsran = self.bot.commands_ran
            marklist = sorted(cmdsran.items(), key=lambda x: x[1], reverse=True)
            sortdict = dict(marklist)
            p = ctx.prefix
            value_iterator = iter(sortdict.values())
            key_iterator = iter(sortdict.keys())
            emby = discord.Embed(title='edoC command Stats',
                                 description=f'{self.bot.total_commands_ran} Commands ran this boot\n',
                                 color=random_color())
            emby.add_field(name='Top 10 commands ran',
                           value=f'🥇:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🥈:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🥉:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n'
                                 f'🏅:{p}{next(key_iterator)} ({next(value_iterator)} uses)\n')

            emby.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)

            await ctx.reply('hi', embed=emby)
        except StopIteration as e:
            await ctx.send(f'{e} e')

    @commands.command(hidden=True)
    @commands.cooldown(rate=2, per=300, type=commands.BucketType.user)
    async def Yellow(self, ctx):
        """Allows you to Toggle having the yellow role"""
        await toggle_role(ctx, 879084837451993099)

    @commands.command(aliases=['credits'])
    async def contributors(self, ctx):
        emb = discord.Embed(title=f'Contributors Of edoC', color=random_color(), description='')
        emb.set_footer(text='Created by Jake CEO of annoyance#1904',
                       icon_url=self.bot.get_user(511724576674414600).display_avatar.url)
        for k, v in contributors.items():
            emb.add_field(name=f'***{k}***', value=f'{v}', inline=False)
        await ctx.send(embed=emb)

    # ~~~
    @commands.command(name='in', aliases=["stats", "status", "botinfo", 'info', 'about'])
    async def _in(self, ctx):
        """ edoC information/stats cmd """
        lines = fetch_info()
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)
        comments = lines.get('total_python_comments')
        coro = lines.get('total_python_coroutines')
        func = lines.get('total_python_functions')
        clas = lines.get('total_python_class')
        tlines = lines.get('total_lines')
        files = lines.get('file_amount')
        pyfiles = lines.get('python_file_amount')
        lang = 'ahk'
        prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?",
                          ctx.guild.id)  # get_prefix(self.bot, ctx)
        cmds = self.bot.total_commands_ran
        chancount = str(len(list(self.bot.get_all_channels())))
        infos = {}
        #define em all lmao

        infos[f'{emoji("dev")}Developer'] = f'ini\n{version_info["dev"]}'
        infos[f'{status(str(ctx.guild.me.status))} Uptime'] = precisedelta(discord.utils.utcnow() - self.bot.start_time,
                                                                           format='%.0f')
        infos[f'System'] = system()
        infos[
            'Stats'] = f'{lang}\nMember Count: {sum(g.member_count for g in self.bot.guilds)}\nChannel Count: {chancount}\n' \
                       f'Guild Count: {len(self.bot.guilds)}\nAvg users/server: {avgmembers:,.2f}\n' \
                       f'Commands Loaded: {len([x.name for x in self.bot.commands])}\nCommands Ran this boot: {cmds}'

        infos['Lines'] = f"""{lang}\n
Python Files: {pyfiles}
Files: {files}
Lines: {tlines}
Classes: {clas}
Functions: {func}
Coroutines: {coro}
Comments: {comments}"""
        infos["__Latest changes__"] = version_info["info"].title()
        infemb = discord.Embed(color=invis, description='')
        async with ctx.channel.typing():
            infemb.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar,
                              url='https://github.com/JakeWasChosen/edoC')
            infemb.set_thumbnail(url=ctx.guild.me.avatar)
            for k, v in infos.items():
                infemb.add_field(name=k, value=f'```{v}```', inline=False)
            infemb.add_field(name='<:dpy:596577034537402378> Discord.py version', value=f'```{discord.__version__}```')
            infemb.add_field(name='<:python:868285625877557379> Python Version', value=f'```{python_version()}```')
            infemb.add_field(name='<:edoC:874868276256202782> edoC Version', value=f'```{version_info["version"]}```')
            infemb.description += ":link: __Links__ \n" \
                                  "  [dev links](https://bio.link/edoC) " \
                                  "| [support me](https://www.buymeacoffee.com/edoC) " \
                                  "| [invite](https://discordapp.com/oauth2/authorize?cient_id=845186772698923029&scope=bot&permissions=8) "
            infemb.set_footer(text=f"Prefix in this server: {prefix}")
        await ctx.reply(embed=infemb)

    @commands.command(aliases=["SAF"])
    @commands.has_permissions(attach_files=True)
    async def sendasfile(self, ctx, *, text: str):
        """ sends whatever the user sent as a file"""
        data = BytesIO(text.encode("utf-8"))
        await ctx.reply(file=discord.File(data, filename=f"{timetext('Text')}"))

    @commands.command(aliases=["SAFF"])
    @commands.has_permissions(attach_files=True)
    async def sendasformatedfile(self, ctx, filetype: str, *, text: str):
        """ sends whatever the user sent as a file BUT with a specified filetype"""
        data = BytesIO(text.encode("utf-8"))
        await ctx.reply(file=discord.File(data, filename=f"{CustomTimetext(filetype, 'Text')}"))

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
        p = Path('./')
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

        infos = fetch_info()
        l = infos.get('total_lines')
        cl = infos.get('total_python_class')
        func = infos.get('total_python_functions')
        coru = infos.get('total_python_coroutines')
        com = infos.get('total_python_comments')
        fc = infos.get('file_amount')
        pyfc = infos.get('python_file_amount')

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
        e.description = f"```{lang}\nPython Files: {pyfc}\nFiles: {fc}\nLines: {l:,}\nClasses: {cl}\nFunctions: {func}\nCoroutines: {coru}\nComments: {com:,}```"
        e.set_footer(text=f"Requested by {ctx.author.name}\n{embedfooter}")
        await ctx.send(embed=e)

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
    async def repo(self, ctx):
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
        info["Python Version"] = f"{python_version()}"
        info["Avg users/server"] = f"{avgmembers:,.2f}"
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
