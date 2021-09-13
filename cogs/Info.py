# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import asyncio
import contextlib
import inspect
from datetime import datetime as dt
from datetime import timezone
from os import path
from pathlib import Path
from platform import python_version, system
from random import choice
from textwrap import dedent
from typing import List, Tuple

from PyDictionary import PyDictionary
from discord import HTTPException
from discord.ext.commands import ColourConverter, command, Cog, BucketType, cooldown, BadArgument, has_permissions, \
    clean_content
from discord.ext.menus import ListPageSource
from googletrans import Translator
from humanize import precisedelta, naturaltime as nt
from pyshorteners import Shortener
from textblob import TextBlob

from utils.apis.mojang.mojang import MojangAPI as MoI
from utils.checks import guild_only, UrlSafe
from utils.curse import ProfanitiesFilter
from utils.default import *
from utils.http import get
from utils.info import fetch_info
from utils.pagination import IndexedListSource, CatchAllMenu
from utils.text_formatting import hyperlink
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


def no_dict(word):
    w = str(word)
    return w.replace("['", '').replace("']", '').replace("'", '')


def meanings(word):
    toreturn = ''
    count = 0
    word = no_dict(word)
    print(word)
    for wrd in word.split(','):
        count += 1
        toreturn += f'\n**#{count}** {wrd}'
    return toreturn if len(toreturn) > 1 else word


class Info(Cog, description='Informational and useful commands'):
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
        self.pf = ProfanitiesFilter()
        self.pf.inside_words = True
        self.dict = PyDictionary()
        self.db = self.bot.db

    async def get_word(self, ctx, word: UrlSafe):
        async with ctx.session.get(f"https://some-random-api.ml/dictionary?word={word}") as ses:
            if ses.status != 200:
                if ses.status == 404:
                    return await ctx.error('Word Not found.')
                elif ses.status == 429:
                    return await ctx.error(f'Too many requests, please try again later.')
        return await ses.json()

    @command(aliases=['McUser', 'MCI'], brief='Gets info about a minecraft user')
    async def mcinfo(self, ctx, user: str):
        uuid = await MoI.get_uuid(user)
        if not uuid:
            return await ctx.error(f'User **{user}** Doesnt exist')
        prof = await MoI.get_profile(uuid)
        em = Embed(color=random_color()).set_image(url=f'https://minotar.net/armor/body/{prof.name}/550.png')
        em.description = f'**UUID :** {uuid}\n' \
                         f'**Skin Type :** {prof.skin_model}\n' \
                         f'**Legacy Profile :** {prof.is_legacy_profile}\n' \
                         f'{hyperlink("Skin Url", prof.skin_url)}'
        em.set_author(name=f'Info About {prof.name}', url=f'https://namemc.com/profile/{prof.name}', icon_url=f'https://minotar.net/helm/{prof.name}/25.png')
        namehistory = await MoI.get_name_history(uuid)
        names = ''
        for name in reversed(namehistory):
            ts = name["changed_to_at"]
            if ts == 0:
                names += f'\n**{name["name"]} :** Original name'
                continue
            ts /= 1000
            names += f'\n**{name["name"]} :** <t:{int(ts)}:R>'
        em.add_field(name='Name Histoy', value=names, inline=False)
        await ctx.try_reply(embed=em)
    @command(aliases=['spelling', 'fixspelling', 'autocorrect'], brief='Corrects the spelling of the input')
    async def correct(self, ctx, *, words: str):
        tb = TextBlob(text=words)
        await ctx.invis(str(tb.correct()))

    @command(aliases=("spotify", "spot"),
             brief="Show what song a member listening to in Spotify", )
    @cooldown(1, 5, BucketType.user)
    @guild_only()
    async def spotifyinfo(self, ctx, user: discord.Member = None):
        user = user or ctx.author

        spotify: discord.Spotify = discord.utils.find(
            lambda s: isinstance(s, discord.Spotify), user.activities
        )
        if not spotify:
            return await ctx.error(
                f"{user} is not listening to Spotify!"
            )

        e = (
            Embed(
                title=spotify.title,
                colour=spotify.colour,
                url=f"https://open.spotify.com/track/{spotify.track_id}"
            ).set_author(name="Spotify", icon_url="https://i.imgur.com/PA3vvdN.png"
                         ).set_thumbnail(url=spotify.album_cover_url)
        )

        # duration
        cur, dur = (
            utcnow() - spotify.start.replace(tzinfo=timezone.utc),
            spotify.duration,
        )

        # Bar stuff
        barLength = 5 if user.is_on_mobile() else 17
        bar = renderBar(
            int((cur.seconds / dur.seconds) * 100),
            fill="─",
            empty="─",
            point="⬤",
            length=barLength,
        )

        e.add_field(name="Artist", value=", ".join(spotify.artists))

        e.add_field(name="Album", value=spotify.album)

        e.add_field(
            name="Duration",
            value=(
                    f"{cur.seconds // 60:02}:{cur.seconds % 60:02}"
                    + f" {bar} "
                    + f"{dur.seconds // 60:02}:"
                    + f"{dur.seconds % 60:02}"
            ),
            inline=False,
        )
        await ctx.try_reply(embed=e)

    async def create_embed(self, description, field: List[Tuple] = None):
        embed_ = discord.Embed(description=description,
                               colour=orange)
        if field is not None:
            for name, value, inline in field:
                embed_.add_field(name=name, value=value, inline=inline)
        return embed_

    @command(aliases=['definiton', 'meaning'])
    async def word(self, ctx, *, word: str):
        # data = await self.get_word(ctx, word)
        # await ctx.invis(type(data))
        # em = Embed(title=data['word'], description=data['definition'], color=invis)
        # await ctx.try_reply(embed=em)
        # other
        return await ctx.error('placeholder')

    @command(aliases=['trans'])
    async def translate(self, ctx, *, message: clean_content = None):
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

    @command(name="report")
    async def _report(self, ctx):
        """Used to report something."""
        questions = [
            "What do you want to report?",
            "Write a descriptive overview of what you are reporting.\n"
            "Note that your answer must be about 20 characters.",
        ]
        answers = []
        for question in questions:
            await ctx.send(question)
            try:
                answer = await self.bot.wait_for(
                    "message",
                    timeout=60,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                )
            except asyncio.TimeoutError:
                raise BadArgument(
                    "`60s` are over. I ended your report session, "
                    "since you didn't answer fast enough. Please be quicker next time."
                )
            else:
                answer = answer.content
                answers.append(answer)

        if len(answers[1]) < 20:
            raise BadArgument("Sorry, your answer must be a little longer.")
        if answers:
            em = Embed(title=answers[0], description=answers[1], timestamp=datetime.utcnow())
            em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            em.set_footer(text="ID: " + str(ctx.author.id))
            msg = await ctx.send(
                content="Are you sure you want to submit your report?", embed=em
            )
            for emoji in (emojis := [self.bot.icons['greenTick'], self.bot.icons['redTick']]): await msg.add_reaction(
                emoji)
            try:
                reaction, m = await self.bot.wait_for(
                    "reaction_add",
                    timeout=45,
                    check=lambda reaction, m: m == ctx.author
                                              and str(reaction.emoji) in emojis,
                )
                if str(reaction) == self.bot.icons['greenTick']:
                    channel = self.bot.get_channel(877724111420391515)
                    await channel.send(embed=em)
                    return await ctx.send("Submitted your report")
                else:
                    return await ctx.send("Cancelled your report.")
            except asyncio.TimeoutError:
                raise BadArgument(
                    "`60s` are over. I ended your report session, since you didn't answer fast enough. Next time please be quicker."
                )

    @command(name="suggest")
    async def _suggest_feature(self, ctx, *, suggestion: str):
        """Used to suggest a feature for edoC."""
        channel = self.bot.get_channel(878486511794929664)
        if len(suggestion) > 300:
            return await ctx.error('Too Long please keep under 300 characters')
        elif len(suggestion) < 20:
            return await ctx.warn('Too short please keep over 20 characters')
        e = Embed(color=green)
        e.description = self.pf.clean(suggestion)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        msg = await channel.send(embed=e)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await ctx.send(f"Submitted your suggestion. Join the support server to see the status of your suggestion.")

    @command()
    async def nohi(self, ctx):
        await ctx.try_reply('https://nohello.net/')

    @command(brief="Shows the bot's uptime")
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

    @command(aliases=['RC', 'Rcolor', 'RandColor'])
    async def RandomColor(self, ctx):
        random_number = randint(0, 16777215)
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

    @command(aliases=['C', 'Colour'])
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
        if isinstance(error, BadArgument):
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

    # @command(aliases=["todomenu"])
    # async def todo(self, ctx):
    #     """Shows this message."""
    #     file = open("todo.txt", "r")
    #     embeds = []
    #     if len(list(file)) <= 2000:
    #         return await ctx.reply(embed=discord.Embed(
    #             title="TodoPagination",
    #             color=blue,
    #             description=file.readlines()))
    #     i = 0
    #
    #     while True:
    #         filelines = len(file.readlines())
    #         if len(list(file)) - i > 200:
    #             embeds.append(discord.Embed(
    #                 title="TodoPagination",
    #                 description=list(file)[i:i + 1999],
    #                 color=blue))
    #         elif len(list(file)) - i <= 0:
    #             break
    #         else:
    #             embeds.append(discord.Embed(
    #                 title="TodoPagination",
    #                 description=list(file)[i:len(list(file)) - 1],
    #                 color=blue))
    #             break
    #         i += 1999
    #
    #     return await ctx.reply(embed=embeds[0], view=Paginator(ctx=ctx, embeds=embeds))
    async def get_all_todo(self, identifier: int = None):
        if not identifier:
            return self.db.fetch("SELECT * FROM todo")
        else:
            return self.db.fetch("SELECT * FROM todo WHERE user_id = ?", (identifier,))

    @commands.group(invoke_without_command=True)
    async def todo(self, ctx):
        """Shows your current todo list"""
        items = []
        results = sorted((await self.get_all_todo(ctx.author.id)), key=lambda x: x['time'])
        for each in results:
            time = dt.utcfromtimestamp(each['time'])
            since = nt(dt.utcnow() - time)
            if each['description']:
                desc_em = "`\U00002754`"
            else:
                desc_em = ""
            items.append(f"[{each['todo']}]({each['message_url']}) (ID: {each['id']} | Created {since}) {desc_em}")
        source = IndexedListSource(data=items, embed=discord.Embed(colour=invis),
                                   title="Items (`\U00002754` indicates that the todo has a description)", per_page=5)
        menu = CatchAllMenu(source=source)
        menu.add_info_fields({"`\U00002754`": "Indicates that the todo has a description"})
        await menu.start(ctx)

    @todo.command()
    async def add(self, ctx, *, todo):
        """Adds an item to your todo list"""
        if len(todo) > 50:
            return await ctx.send("Your todo is too long. Please be more consice.")
        id = randint(1, 99999)
        await self.bot.db.execute(
            "INSERT INTO todo (todo, id, time, message_url, user_id) VALUES ($1, $2, $3, $4, $5)", todo, id,
            time.time(),
            str(ctx.message.jump_url), ctx.author.id)
        await ctx.send(f"{ctx.tick()} Inserted `{todo}` into your todo list! (ID: `{id}`)")

    @todo.command(aliases=['rm', 'remove'])
    async def resolve(self, ctx, *id: int):
        """Resolves an item from your todo list"""
        items = await self.get_all_todo(ctx.author.id)
        todos = [item[0] for item in items]
        ids = [item[1] for item in items]
        if any(item not in ids for item in id):
            return await ctx.send("You passed in invalid id's!")
        message = []
        for i in id:
            message.append(f"• {todos[ids.index(i)]}")
            await self.bot.db.execute("DELETE FROM todo WHERE user_id = $1 AND id = $2", ctx.author.id, i)
        await ctx.send(
            f"{ctx.tick()} Deleted **{len(id)}** items from your todo list:\n" + "\n".join(message))

    @todo.command()
    async def list(self, ctx):
        """Shows your todo list"""
        command = self.bot.get_command('todo')
        await ctx.invoke(command)

    @todo.command()
    async def clear(self, ctx):
        """Clears all of your todos"""
        num = len((await self.bot.db.fetch("SELECT * FROM todo WHERE user_id = $1", ctx.author.id)))
        await self.bot.db.execute("DELETE FROM todo WHERE user_id = $1", ctx.author.id)
        await ctx.send(f"{ctx.tick()} Deleted **{num}** items from your todo list!")

    @todo.command(aliases=['show'])
    async def info(self, ctx, id: int):
        """Shows you info on a todo"""
        results = await self.bot.db.fetch("SELECT * FROM todo WHERE id = $1", id)
        if not results:
            raise commands.BadArgument(f'{id} is not a valid todo!')
        results = results[0]
        embed = discord.Embed(colour=self.bot.colour)
        embed.title = f"{results['todo']} » `{results['id']}`"
        time = dt.utcfromtimestamp(results['time'])
        since = nt(dt.utcnow() - time)
        embed.description = f'{results["description"] or ""}\n'
        embed.description += f"<:clock:738186842343735387> **{since}**\n"
        embed.description += f"**{time.strftime('%A %B %d, %Y at %I:%M %p')}**"
        await ctx.send(embed=embed)

    @todo.command(aliases=['add_desc', 'ad'])
    async def describe(self, ctx, id: int, *, description):
        """Add a description for your todo"""
        results = await self.bot.db.fetch("SELECT * FROM todo WHERE id = $1", id)
        if not results:
            raise commands.BadArgument(f'{id} is not a valid todo!')
        if len(description) > 250:
            return await ctx.send("That description is too long!")
        await self.bot.db.execute("UPDATE todo SET description = $1 WHERE id = $2", description, id)
        await ctx.send(
            f"{ctx.tick()} Set todo description for `{id}` ({results[0]['todo']}) to `{description}`")

    @command(aliases=['len'])
    async def length(self, ctx, *, word):
        await ctx.reply(len(word))

    @command(aliases=["URLshorten"])
    async def shorten(self, ctx, *, url):
        s = Shortener()
        ShortenedUrl = s.owly.short(url)
        await ctx.reply(embed=discord.Embed(description=ShortenedUrl, colour=random_color()))

    @command(aliases=["URLexpand"])
    async def expand(self, ctx, *, url):
        s = Shortener()
        ExpandedUrl = s.owly.expand(url)
        await ctx.reply(embed=discord.Embed(description=ExpandedUrl, colour=random_color()))

    # @command()
    # async def time(self, ctx):
    #    """ Check what the time is for me (the bot) """
    #    time = datetime.utcnow().strftime("%d %B %Y, %H:%M")
    #    await ctx.send(f"Currently the time for me is **{time}**")

    # ~~~~~~~~~~~~~~~~~~~~~~~~
    @command()
    # @cooldown(rate=1, per=300, type=BucketType.guild)
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

    @command(hidden=True)
    @cooldown(rate=2, per=300, type=BucketType.user)
    async def Yellow(self, ctx):
        """Allows you to Toggle having the yellow role"""
        await toggle_role(ctx, 879084837451993099)

    @command(aliases=['credits'])
    async def contributors(self, ctx):
        emb = discord.Embed(title=f'Contributors Of edoC', color=random_color(), description='')
        emb.set_footer(text='Created by Jake CEO of annoyance#1904',
                       icon_url=self.bot.get_user(511724576674414600).display_avatar.url)
        for k, v in contributors.items():
            emb.add_field(name=f'***{k}***', value=f'{v}', inline=False)
        await ctx.send(embed=emb)

    @command()
    async def donate(self, ctx):
        class DonateView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.add_item(discord.ui.Button(label='Ko-Fi', url='https://ko-fi.com/edocthebot'))
                self.add_item(discord.ui.Button(label='Buy me a coffee', url='https://www.buymeacoffee.com/edoC'))

        em = Embed(title='Donate to edoC', color=invis)
        em.set_thumbnail(url=self.bot.user.avatar.url)
        em.description = 'Donating money to edoC will help out the developer a lot with service fees for edoC among others. \
                         Note that this is not required to access any exclusive content on the bot! \
                         The sole purpose of donating is to support edoC\'s development.'

        await ctx.send(embed=em, view=DonateView())

    # ~~~
    @command(name='in', aliases=["stats", "status", "botinfo", 'info', 'about'])
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
        # define em all lmao

        infos[f'{emoji("dev")}Developer'] = f'ini\n{version_info["dev"]}'
        infos[f'{status(str(ctx.guild.me.status))} Uptime'] = precisedelta(discord.utils.utcnow() - self.bot.start_time,
                                                                           format='%.0f')
        infos[f'System'] = system()
        infos[
            'Stats'] = f'{lang}\nMember Count: {sum(g.member_count for g in self.bot.guilds)}\nChannel Count: {chancount}\n' \
                       f'Guild Count: {len(self.bot.guilds)}\nAvg users/server: {avgmembers:,.2f}\n' \
                       f'Commands Loaded: {len([x.name for x in self.bot.commands])}\nCommands Ran this boot: {cmds}\n' \
                       f'Total Messages seen: {self.bot.seen_messages:,}'

        infos['Lines'] = f"""{lang}\n
Python Files: {pyfiles}
Files: {files}
Lines: {tlines}
Classes: {clas}
Functions: {func}
Coroutines: {coro}
Comments: {comments}"""
        infos["Latest changes"] = version_info["info"].title()
        infemb = discord.Embed(color=invis, description='')
        async with ctx.channel.typing():
            infemb.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar,
                              url='https://github.com/JakeWasChosen/edoC')
            infemb.set_thumbnail(url=self.bot.user.avatar)
            for k, v in infos.items():
                infemb.add_field(name=k, value=f'```{v}```', inline=False)
            infemb.add_field(name='<:dpy:596577034537402378> Discord.py version', value=f'```{discord.__version__}```')
            infemb.add_field(name='<:python:868285625877557379> Python Version', value=f'```{python_version()}```')
            infemb.add_field(name='<:edoC:874868276256202782> edoC Version', value=f'```{version_info["version"]}```')
            infemb.description += ":link: **Links** \n" \
                                  "  [dev links](https://bio.link/edoC) " \
                                  "| [support me](https://www.buymeacoffee.com/edoC) " \
                                  "| [invite](https://discord.com/api/oauth2/authorize?client_id=845186772698923029&permissions=8&scope=bot%20applications.commands)"
            infemb.set_footer(text=f"Prefix in this server: {prefix}")
        await ctx.reply(embed=infemb)

    @command(aliases=["SAF"])
    @has_permissions(attach_files=True)
    async def sendasfile(self, ctx, *, text: str):
        """ sends whatever the user sent as a file"""
        data = BytesIO(text.encode("utf-8"))
        await ctx.reply(file=discord.File(data, filename=f"{timetext('Text')}"))

    @command(aliases=["SAFF"])
    @has_permissions(attach_files=True)
    async def sendasformatedfile(self, ctx, filetype: str, *, text: str):
        """ sends whatever the user sent as a file BUT with a specified filetype"""
        data = BytesIO(text.encode("utf-8"))
        await ctx.reply(file=discord.File(data, filename=f"{CustomTimetext(filetype, 'Text')}"))

    @command(aliases=['src'])
    async def source(self, ctx, *, command: str = None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. cat.hi for the hi subcommand of the cat command
        or by spaces.
        """
        source_url = 'https://github.com/JakeWasChosen/edoC'
        branch = 'main'
        if command is None:
            return await ctx.send(source_url)

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        src = obj.callback.__code__
        filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        location = path.relpath(filename).replace('\\', '/')

        final_url = f'{source_url}/tree/{branch}/main/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}'

        class SourceView(discord.ui.View):
            def __init__(self, ctx):
                super().__init__()
                self.ctx = ctx
                self.add_item(discord.ui.Button(label='Source URL', url=final_url))

            @discord.ui.button(emoji='<:trashcan:882779835737460846>')
            async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user != self.ctx.author:
                    return await interaction.response.send_message('Oops. This is not your interaction.',
                                                                   ephemeral=True)
                with contextlib.suppress(discord.HTTPException):
                    await self.ctx.message.delete()
                await interaction.message.delete()

            @discord.ui.button(label='Source File')
            async def send_file(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user != self.ctx.author:
                    return await interaction.response.send_message('Oops. This is not your interaction.',
                                                                   ephemeral=True)

                await interaction.channel.send(
                    file=discord.File(BytesIO(dedent(''.join(lines)).encode('ascii')), 'source.py'))
                button.disabled = True
                await interaction.response.edit_message(view=self)

        em = Embed(title=f'Here is the source for {obj.qualified_name}')

        if len("".join(lines)) < 2000:
            zwsp = '\u200b'
            em.description = f'```py\n{dedent("".join(lines).replace("``", f"`{zwsp}`"))}\n```'
        else:
            em.description = '```\nSource was too long to be shown here. Click Source File/Source URL below to see it.```'
        await ctx.send(embed=em, view=SourceView(ctx))

    @command(help="Shows the bot's latency in miliseconds.Useful if you want to know if the bot is lagging or not",
             brief="Shows the bots latency")
    async def ping(self, ctx):
        start = time.perf_counter()
        msg = await ctx.invis("<a:disloading:879146777767473174> pinging...")
        end = time.perf_counter()
        typing_ping = (end - start) * 1000

        # start = time.perf_counter()
        # self.db.execute('SELECT 1')
        # end = time.perf_counter()
        # sql_ping = (end - start) * 1000
        e = discord.Embed(
            description=f"{self.bot.icons['typing']} ** | Typing**: {round(typing_ping, 1)} ms\n{self.bot.icons['edoc']} ** | Websocket**: {round(self.bot.latency * 1000)} ms",
            color=invis)  # \n{self.bot.icons['database']} **" | Database**: {round(sql_ping, 1)} ms")
        await msg.edit(embed=e)

    @command()
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

        lang = choice(["ahk", "apache", "prolog"])
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

    @command()
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

    @command(aliases=["code"])
    async def repo(self, ctx):
        """ Check out my source code <3 """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT.
        await ctx.reply(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/JakeWasChosen/edoC")

    @command(aliases=["supportserver", "feedbackserver"])
    async def botserver(self, ctx):
        """ Get an invite to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 819282410213605406:
            return await ctx.send(f"**Here you go {ctx.author.name} 🍻\n<{self.config['botserver']}>**")
        await ctx.reply(f"**{ctx.author.name}** this is my home you know :3")

    @command()
    async def covid(self, ctx, *, country: str):
        """Covid-19 Statistics for any countries"""
        country = country.title()
        async with ctx.channel.typing():
            r = await get(f"https://disease.sh/v3/covid-19/countries/{country.lower()}", res_method="json")

            if "message" in r:
                return await ctx.send(f"The API returned an error:\n{r['message']}")

            json_data = [
                ("Total Cases", r["cases"]), ("Total Deaths", r["deaths"]),
                ("Total Recover", r["recovered"]), ("Total Active Cases", r["active"]),
                ("Total Critical Condition", r["critical"]), ("New Cases Today", r["todayCases"]),
                ("New Deaths Today", r["todayDeaths"]), ("New Recovery Today", r["todayRecovered"])
            ]

            embed = discord.Embed(
                description=f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R>"
            )

            for name, value in json_data:
                embed.add_field(
                    name=name, value=f"{value:,}" if isinstance(value, int) else value
                )

            await ctx.send(
                f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
                f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
                embed=embed
            )

    @command(aliases=["bs"])
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

    @guild_only()
    @command()
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
    bot.add_cog(Info(bot))
