# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import asyncio
import json
from asyncio import sleep
from collections import Counter
from io import BytesIO
from random import *
from secrets import token_urlsafe
from typing import Optional

import discord
import discord.ext.commands
from aiotrivia import TriviaClient, AiotriviaException
from bs4 import BeautifulSoup
from discord import Embed, HTTPException
from discord.ext import commands
from discord.ext.commands import BucketType, command, max_concurrency, cooldown
from discord.ext.menus import MenuPages
from faker import Faker
from nekos import InvalidArgument, why, owoify, img
from phone_gen import PhoneNumber
from pyfiglet import figlet_format
from pyjokes import pyjokes

from cogs.Discordinfo import plural
from utils.apis.Somerandomapi import SRA
from utils.checks import MemberConverterr
from utils.default import config, CustomTimetext
from utils.http import get
from utils.pagination import UrbanSource
from utils.vars import *


class Fun(commands.Cog, description='Fun and entertaining commands can be found below'):
    def __init__(self, bot):
        self.bot = bot
        self.config = config()
        self.alex_api_token = self.config["alexflipnote_api"]
        self.trivia = TriviaClient()
        self.sra = SRA(session=self.bot.session)

    @command()
    async def trivia(self, ctx, difficulty: str):
        difficulty = difficulty.lower()
        try:
            question = await self.trivia.get_random_question(difficulty)
        except AiotriviaException as error:
            if error.__class__.__name__ == 'InvalidDifficulty':
                return await ctx.error('Invalid Difficulty Please use either easy, medium or hard')
            return await ctx.error(f"{error.__class__.__name__}: {error}")
        answers = question.responses
        shuffle(answers)
        final_answers = '\n'.join([f"{index}. {value}" for index, value in enumerate(answers, 1)])
        message = await ctx.invis(
            f"**{question.question}**\n{final_answers}\n{question.type.capitalize()} Question about {question.category}")
        answer = answers.index(question.answer) + 1
        await self.trivia.close()  # cleaning up
        try:
            while True:
                msg = await self.bot.wait_for('message', timeout=15, check=lambda m: m.id != message.id)
                if str(answer) in msg.content:
                    return await ctx.success(f"{answer} was correct! ({question.answer})")
        except asyncio.TimeoutError:
            await ctx.invis(f"The correct answer was {question.answer}")

    @commands.command(aliases=["sayagain", 'repeat'])
    async def echo(self, ctx, *, what_to_say: commands.clean_content):
        """ repeats text """
        await ctx.reply(f'🦜 {what_to_say}')

    @commands.command(aliases=["8ball"])
    async def eightball(self, ctx, *, question: commands.clean_content):
        """ Consult 8ball to receive an answer """
        answer = choice(ballresponse)
        tosend = f"🎱 **Question:** {question}\n**Answer:** {answer}"
        emb = discord.Embed(description=tosend, color=choice(ColorsList))
        await ctx.reply(embed=emb)

    @command(aliases=['ouija'], brief="Asks the mystical Ouija Board a question...")
    async def askouija(self, ctx, *, question: str):
        ouija_choice = choice(ouija_responses)
        ouija_says = f"You asked me... '_{question}_'... I respond... {ouija_choice}"
        await ctx.success(ouija_says)

    @commands.command(aliases=['asciiart'])
    async def ascii(self, ctx, *, value):
        """ sends ascii style art """
        art = figlet_format(f"{value}")
        try:
            await ctx.send(f"```\n{art}```")
        except HTTPException:
            await ctx.send('Thats a bit too long please try somthing shorter')
        else:
            return await ctx.error(
                'please join the support server and ping the developer about this (i think there will be an error here sometime)')

    @commands.command(aliases=["roll", "dice"])
    async def rolldice(self, ctx, guess):
        answer = randint(1, 6)
        await ctx.reply(embed=discord.Embed(color=green if guess == answer else red,
                                            description=f"{'True' if guess == answer else 'False'} your guess was {guess} and the answer was {answer}"))

    @commands.command()
    async def rip(self, ctx, name: str = None, *, text: str = None):
        """ Sends a tombstone with a name with x text under
        E.g. ~rip (dev)Jason **FREE** *at last..*"""

        if name is None:
            name = ctx.message.author.name
        if len(ctx.message.mentions) >= 1:
            name = ctx.message.mentions[0].name
        if text is not None:
            if len(text) > 22:
                one = text[:22]
                two = text[22:]
                url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4={1}&top5={2}".format(name,
                                                                                                                  one,
                                                                                                                  two).replace(
                    " ", "%20")
            else:
                url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4={1}".format(name,
                                                                                                         text).replace(
                    " ", "%20")
        else:
            if name[-1].lower() != 's':
                name += "'s"
            url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4=Hopes and Dreams".format(
                name).replace(" ", "%20")
        await ctx.send(url)

    @commands.command(aliases=['achievement', 'ach'])
    async def mc(self, ctx, *, txt: str):
        """Generate a Minecraft Achievement"""
        author = ctx.author.display_name if len(ctx.author.display_name) < 22 else "Achievement Unlocked!"
        t = txt.replace(' ', '+')
        a = author.replace(' ', '+')
        if len(txt) > 25:
            return await ErrorEmbed(ctx, err="Please keep your message under 25 chars")
        api = f'https://mcgen.herokuapp.com/a.php?i=2&h={a}&t={t}'
        emb = discord.Embed(color=random_color())
        emb.set_image(url=api)
        await ctx.reply(embed=emb)

    @commands.command(aliases=["rfact", "rf"])
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    async def RandomFact(self, ctx):
        """ Legit just posts a random fact"""
        fact = choice(random_facts)
        emb = discord.Embed(description=fact, color=choice(ColorsList))
        await ctx.reply(embed=emb, mention_author=False)

    async def api_img_creator(self, ctx, url: str, filename: str, content: str = None):
        async with ctx.channel.typing():
            req = await get(url, res_method="read")

            if not req:
                return await ctx.send("I couldn't create the image ;-;")

            bio = BytesIO(req)
            bio.seek(0)
            await ctx.send(content=content, file=discord.File(bio, filename=filename))

    # @commands.command(aliases=["doggo"])
    # @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    # async def dog(self, ctx):
    #    """ Posts a random dog """
    #    await self.randomimageapi(ctx, "https://dog/woof.json", "url")

    @commands.command(aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{choice(coinsides)}**!")

    @commands.command(aliases=["flip", "coin"])
    async def coinflip(self, ctx, *, toss='Heads'):
        """ Coinflip! """
        responses = ['Heads', 'Tails']
        if len(toss) > 100:
            return await ErrorEmbed(ctx=ctx, err='Please keep the length of your toss down')
        value = randint(0, 0xffffff)
        embed = discord.Embed(

            colour=value,

        )
        embed.add_field(name=f'**User Side:** {toss}\n**Result:** {choice(responses)}',
                        value="Someone is gonna go cry to mommy.", inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=['Programmingjoke', 'pj'])
    async def ProgrammerHumor(self, ctx):
        """ Just run the command """
        joke = pyjokes.get_joke()
        await ctx.reply(joke)

    @commands.command(aliases=['renamedchuckJokes', 'gudjokesherenoscam', 'CJ'])
    async def ChuckJoke(self, ctx, person: MemberConverterr = None):
        """ChuckNorris is the only man to ever defeat a brick wall in a game of tennis."""
        joke = choice(chuckjoke)
        if person is not None:
            try:
                nj = joke.replace('Chuck Norris', person)
            except TypeError:
                nj = joke.replace('Chuck Norris', ctx.author.display_name)
        else:
            nj = joke
        await ctx.reply(embed=discord.Embed(color=green, description=nj))

    @commands.command(aliases=['quote'])
    async def inspire(self, ctx):
        async with ctx.session.get("https://zenquotes.io/api/random") as api:
            data = await api.read()
        data2 = json.loads(data)
        await ctx.send(embed=discord.Embed(description=data2[0]['q'], color=invis).set_author(name=data2[0]["a"]))

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def topic(self, ctx):
        """ Generates a random topic to start a conversation up"""
        url = "https://www.conversationstarters.com/generator.php"
        async with self.bot.session.get(url) as r:
            output = await r.read()
            soup = BeautifulSoup(output, 'html5lib')
            topics = soup.find("div", {"id": "random"})
            topic = topics.contents[1]
        await ctx.send(f"**{topic}**")

    @commands.command(aliases=["ie"])
    async def iseven(self, ctx, num: int):
        """ checks if a number is even or not"""
        async with ctx.session.get(f'https://api.isevenapi.xyz/api/iseven/{num}/') as api:
            data = await api.json()
        if data["iseven"]:
            color = green
            answer = "Yes"
            answer2 = " "
        else:
            color = red
            answer = "No"
            answer2 = " not"

        embed = discord.Embed(
            title="**IsEven finder**",
            description=f"{answer} {num} is{answer2} even",
            color=color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=data["ad"])
        await ctx.send(embed=embed)

    @commands.command(aliases=['randint', 'rn'])
    async def RandomNumber(self, ctx, minimum=0, maximum=100):
        """Displays a random number within an optional range.
        The minimum must be smaller than the maximum and the maximum number
        accepted is 1000.
        """
        maximum = min(maximum, 1000)
        if minimum >= maximum:
            return await ctx.send('Maximum is smaller than minimum.')

        await ctx.send(randint(minimum, maximum))

    @commands.command(aliases=['random-lenny', 'rl'])
    async def rlenny(self, ctx):
        """Displays a random lenny face."""
        lenny = choice([
            "( ͡° ͜ʖ ͡°)", "( ͠° ͟ʖ ͡°)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ", "( ͡~ ͜ʖ ͡°)",
            "( ͡o ͜ʖ ͡o)", "͡(° ͜ʖ ͡ -)", "( ͡͡ ° ͜ ʖ ͡ °)﻿", "(ง ͠° ͟ل͜ ͡°)ง",
            "ヽ༼ຈل͜ຈ༽ﾉ"
        ])
        await ctx.send(lenny)

    @commands.command(aliases=['pick'])
    async def choose(self, ctx, *choices: commands.clean_content):
        """Chooses between multiple choices.
        To denote multiple choices, you should use double quotes.
        """
        if len(choices) < 2:
            return await ctx.send('Not enough choices to pick from.')

        await ctx.send(choice(choices))

    @commands.command(aliases=['CBO'])
    async def choosebestof(self, ctx, times: Optional[int], *choices: commands.clean_content):
        """Chooses between multiple choices N times.
        To denote multiple choices, you should use double quotes.
        You can only choose up to 10001 times and only the top 15 results are shown.
        """
        if len(choices) < 2:
            return await ctx.send('Not enough choices to pick from.')

        if times is None:
            times = (len(choices) ** 2) + 1

        times = min(10001, max(1, times))
        results = Counter(choice(choices) for i in range(times))
        builder = []
        if len(results) > 15:
            builder.append('Only showing top 15 results...')
        for index, (elem, count) in enumerate(results.most_common(15), start=1):
            builder.append(f'{index}. {elem} ({plural(count):time}, {count / times:.2%})')
        data = '\n'.join(builder)
        data = BytesIO(data.encode("utf-8"))
        await ctx.send(file=discord.File(data, filename=f"{CustomTimetext('prolog', 'output')}"))

    @commands.command(name="guessthenumber", aliases=["gtn"], brief="Guess the number game!")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def gtn(self, ctx):
        """Play a guess the number game! You have three chances to guess the number 1-10"""

        no = randint(1, 10)  # randrange to randint
        await ctx.success(
            "A number between **1 and 10** has been chosen, You have 3 attempts to guess the right number! Type your guess in the chat as a valid number!"
            # no f
        )
        for i in range(3):
            try:
                response = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                )
            except asyncio.TimeoutError:
                await ctx.error(
                    "You got to give me a number... game ended due to inactivity"
                )
                return

            if not response.content.isdigit():
                if 2 - i == 0:
                    await ctx.error(
                        f"Unlucky, you ran out of attempts. The number was **{no}**"
                    )
                    return
                await ctx.error(
                    "That is not a valid number! It costed you one attempt..."
                )
                continue
            guess = int(response.content)

            if guess > 10 or guess < 1:
                await ctx.error(
                    "That number is out of range! It costed you one attempt..."
                )
                continue

            if guess != no and 2 - i == 0:
                await ctx.error(
                    f"Unlucky, you ran out of attempts. The number was **{no}**"
                )
                return

            if guess > no:
                await ctx.warn(
                    f"The number is smaller than {guess}\n`{2 - i}` attempts left"
                )
            elif guess < no:
                await ctx.warn(
                    f"The number is bigger than {guess}\n`{2 - i}` attempts left"
                )

            else:
                await ctx.success(
                    f"Good stuff, you got the number right. I was thinking of **{no}**"
                )
                return

    @commands.command()
    async def clap(self, ctx, *, words: commands.clean_content):
        """ Be a annoying karen with ~clap (DO IT)"""
        tosend = ""
        for word in words.split():
            tosend += f"👏 {word} "
        tosend += "👏"
        await ctx.reply(tosend)

    @commands.command(aliases=['Rcap'])
    async def Mock(self, ctx, *, words):
        """ alternate caps and non caps"""
        tosend = ''
        number = 1  # 1 if you want it to start with a capitol 0 if you want it to start with a lowercase
        for letter in words.lower():
            if number == 1:
                tosend += letter.upper()
                number = 0
            else:
                tosend += letter.lower()
                number = 1
        if ctx.author.id == self.bot.ownerid:
            await ctx.message.delete()
        else:
            tosend += f' ||~ {ctx.message.author.name}||\n'
        await ctx.send(tosend)

    @commands.group()
    async def math(self, ctx):
        """ math related cmds self explanatory don't ask why its in fun"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @math.command(name="add", aliases=["addition"])
    async def math_add(self, ctx, num1: int, num2: int):
        await ctx.send(num1 + num2)

    @math.command(name="sub", aliases=["subtraction"])
    async def math_sub(self, ctx, num1: int, num2: int):
        await ctx.send(num1 - num2)

    @math.command(name="multi", aliases=["multiplication"])
    async def math_multi(self, ctx, num1: int, num2: int):
        await ctx.send(num1 * num2)

    @math.command(name="division", aliases=["divide"])
    async def math_divide(self, ctx, num1: int, num2: int):
        await ctx.send(num1 / num2)

    # @commands.command(aliases=["JumboEmoji"])
    # async def LargenEmoji(self, ctx, emoji):
    #    """Display your favorite emotes in large. currently only works on local emojis"""
    #    emote = commands.f(ctx, emoji)
    #    if emote:
    #        em = discord.Embed(colour=random_color())
    #        em.set_image(url=emote.url)
    #        await ctx.send(embed=em)
    #    else:
    #        await ctx.send(content='\N{HEAVY EXCLAMATION MARK SYMBOL} Only Local Emotes...')
    # Currently works but only local ones

    @commands.command()
    async def f(self, ctx, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{choice(hearts)}")

    @commands.command(aliases=['ans'])
    async def answer(self, ctx):
        """ purely just says yes or no randomly """
        ans = choice(["yes", "no"])
        await ctx.reply(ans)

    @commands.command(aliases=["uwuify", "makeuwu", "makeowo"])
    async def owoify(self, ctx, *, text: commands.clean_content = None):
        """ "owoifes" the text"""
        await ctx.reply(owoify(str(text)))

    @commands.command()
    async def why(self, ctx):
        """ why """
        await ctx.reply(why())

    @commands.command(hidden=True)
    @commands.is_nsfw()
    async def img(self, ctx, imgtype: str):
        peeps = {709086074537771019, 511724576674414600}
        if ctx.author.id not in peeps:
            return
        try:
            await ctx.reply(img(target=imgtype))
        except InvalidArgument:
            await ctx.reply("Please put in the correct arguments ")

    @commands.command()
    async def test(self, ctx):
        """ Test command for testing """
        await ctx.send(f"**{ctx.author.name}** has done the **Test** command Oo")

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """ ~poow ,ffuts esreveR
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    @commands.guild_only()
    async def nuke(self, ctx):
        """ Joke cmd doesnt rly do anything except if the owner runs it"""
        message = await ctx.send("Making server backup then nuking")
        await sleep(.5)
        await message.edit(content="Backup 33% complete")
        await sleep(.5)
        await message.edit(content="Backup 64% complete")
        await sleep(.7)
        await message.edit(content="Backup 86% complete")
        await sleep(.57)
        await message.edit(content="Backup 93% complete")
        await sleep(2)
        await message.delete()

        if ctx.author == ctx.guild.owner or ctx.channel.permissions_for(ctx.author).manage_channel:
            hiarchypos = ctx.channel.position
            cloned = await ctx.channel.clone()
            await ctx.channel.delete()
            channel = cloned
            await channel.edit(position=hiarchypos)
        else:
            channel = ctx.channel
        await channel.send("Backup 100% complete")
        await sleep(.5)
        e = discord.Embed(title="**Nuking everything now**", colour=red)
        e.set_image(url="https://emoji.gg/assets/emoji/7102_NukeExplosion.gif")
        await channel.send(embed=e)

    @command(brief='turn your text into emojis')
    async def emojify(self, ctx, *, message):
        msg = ''
        letters = list(ascii_lowercase)
        for x in message:
            if x in letters:
                msg += f':regional_indicator_{x}:'
            else:
                msg += INDICATOR_NUMS.get(x, x)
        await ctx.success('\u200b' + msg)

    @commands.command()
    async def password(self, ctx, nbytes: int = 18):
        """ Generates a random password string for you

        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if nbytes not in range(3, 1401):
            return await ctx.send("I only accept any numbers between 3-1400")
        if hasattr(ctx, "guild") and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with your random generated password **{ctx.author.name}**")
        await ctx.author.send(f"🎁 **Here is your password:**\n{token_urlsafe(nbytes)}")

    @commands.command()
    async def rate(self, ctx, *, thing: commands.clean_content):
        """ Rates what you desire """
        rateamount = abs(hash(thing))
        re = abs(hash(thing[-1]))
        await ctx.send(f"I'd rate `{thing}` a **{int(str(rateamount)[:2])}.{str(re)[:2]} / 100**")

    @commands.command(aliases=['cd'])
    async def countdown(self, ctx, times: int = 3, *, tosay: str = "Go Go Go"):
        """Counts down max of 10
        but with a default of 3"""

        if times > 10:
            return await ctx.reply(embed=discord.Embed(color=error, description='The number must be between 0 and 10'))

        msg = await ctx.reply(times)
        countdown = times - 1
        await sleep(1)
        for i in range(countdown):
            await msg.edit(content=countdown - i)
            await sleep(1)

        await msg.edit(f'**{tosay}**')

    @commands.command()
    async def ship(self, ctx, person1: commands.clean_content, person2: commands.clean_content):
        """ Rates what you desire """
        ship_amount = uniform(0.0, 100.0)
        if "jake" or "jason" or "edoc" in person1.lower() or person2.lower():
            ship_amount = 69.42069
        await ctx.send(f"`{person1}` and `{person2}` are **{round(ship_amount, 4)} compatible **")

    @command()
    @max_concurrency(1, BucketType.channel)
    @cooldown(1, 1, BucketType.user)
    async def hack(self, ctx, member: discord.Member = None):
        member = member or await ctx.replied_author
        message = await ctx.cembed(0x346c35, f'Hacking {member.mention} ...')
        fake = Faker()
        email = f'{member.name}{randrange(1000, 9999)}@{choice(email_ends)}'.replace(' ', '')
        times = randrange(8, 20)
        password = ''
        for x in range(times):
            password += choice(chars)
        embed = discord.Embed(
            title=f'Succesfully Hacked {member}!',
            description=f'{ctx.author.mention}: Here is what i got from discord\'s DB',
            colour=0x346c35
        )
        country = choice(countrys)
        phnum = PhoneNumber(country)
        phnum = phnum.get_number()
        embed.add_field(name='Login:', value=f'```ahk\nEmail: {email}\nPassword: {password}\nPhone Number: {phnum}```',
                        inline=False)
        embed.add_field(name='Personal:',
                        value=f'```ahk\nIP: {fake.ipv4()}\nCountry: {country}\nCurrent Device: {device}```', inline=False)
        embed.add_field(name='Discord Stuff:',
                        value=f'```ahk\nID: {member.id}\nUsername: {member.name}\nNickname: {member.nick}\nToken: {await self.sra.bot_token(id=member.id)}\nActivity: {member.activity}\nStatus: {member.status}\nTotal Servers: {randrange(1, 100)}\nJoined Discord At: {member.created_at.strftime("%d %b %Y %I:%M")}```',
                        inline=False)
        await asyncio.sleep(10)
        await message.edit(embed=embed)

    @commands.command()
    async def beer(self, ctx, user: MemberConverterr = None, *, reason: commands.clean_content = ""):
        """ Give someone a beer! 🍻 """
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.name}**: paaaarty!🎉🍺")
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you* 🍻")
        if user.bot:
            return await ctx.send(
                f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
        beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
        except TimeoutError:
            await msg.edit(
                content=f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)
        else:
            return await ctx.unknown('uhm unknown error with the beer command', ctx.command)

    @commands.command(aliases=["howhot", "hot"])
    async def hotcalc(self, ctx, *, user: MemberConverterr):
        """ Returns a random percent for how hot is a discord user """
        seed(user.id)
        r = randint(1, 100)
        hot = r / 1.17
        if user.id == 511724576674414600:
            hot = 100

        if hot > 75:
            emoji = "💞"
        elif hot > 50:
            emoji = "💖"
        elif hot > 25:
            emoji = "❤"
        else:
            emoji = "💔"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command(aliases=["memes"], brief="Shows a meme from reddit")
    @commands.cooldown(1, 1.5, type=BucketType.user)
    async def meme(self, ctx):
        """Shows a meme from r/memes."""
        res = await ctx.session.get("https://www.reddit.com/r/memes/random/.json")
        data = await res.json()
        image = data[0]["data"]["children"][0]["data"]["url"]
        permalink = data[0]["data"]["children"][0]["data"]["permalink"]
        url = f"https://reddit.com{permalink}"
        title = data[0]["data"]["children"][0]["data"]["title"]
        ups = data[0]["data"]["children"][0]["data"]["ups"]
        # downs = data[0]["data"]["children"][0]["data"]["downs"]
        comments = data[0]["data"]["children"][0]["data"]["num_comments"]

        em = Embed(colour=discord.Color.blurple(), title=title, url=url)
        em.set_image(url=image)
        em.description = f"<:UpVote:878877980003270686> {ups} <:comment:882798531121913857> {comments}"

        await ctx.send(embed=em)

    @commands.command(name="fight")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def fight(self, ctx, member: MemberConverterr):
        """
        Challenge an user to a duel!
        The user cannot be a bot.
        """
        if member.bot or member == ctx.author:
            return await ctx.send("You can't fight yourself or a bot stupid")

        users = [ctx.author, member]

        user1 = choice(users)
        user2 = ctx.author if user1 == member else member

        user1_hp = 100
        user2_hp = 100

        fails_user1 = 0
        fails_user2 = 0

        x = 2

        while True:
            if user1_hp <= 0 or user2_hp <= 0:
                winner = user1 if user2_hp <= 0 else user2
                loser = user2 if winner == user1 else user1
                winner_hp = user1_hp if user2_hp <= 0 else user2_hp
                await ctx.send(
                    choice(
                        [
                            f"Wow! **{winner.name}** totally melted down **{loser.name}**, winning with just `{winner_hp} HP` left!",
                            f"YEET! **{winner.name}** REKT **{loser.name}**, winning with `{winner_hp} HP` left.",
                            f"Woops! **{winner.name}** send **{loser.name}** home crying... with only `{winner_hp} HP` left!",
                            f"Holy cow! **{winner.name}** won from **{loser.name}** with `{winner_hp} HP` left. **{loser.name}** ran home to their mommy.",
                        ]
                    )
                )
                return

            alpha = user1 if x % 2 == 0 else user2
            beta = user2 if alpha == user1 else user1
            await ctx.send(
                f"{alpha.mention}, what do you want to do? `punch`, `kick`, `slap` or `end`?\nType your choice out in chat as it's displayed!"
            )

            def check(m):
                if alpha == user1:
                    return m.author == user1 and m.channel == ctx.channel
                else:
                    return m.author == user2 and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for("message", timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send(
                    f"**{alpha.name}** didn't react on time. What a noob. **{beta.name}** wins!"
                )
                return

            if msg.content.lower() == "punch":
                damage = choice(
                    [
                        randint(20, 60),
                        randint(0, 50),
                        randint(30, 70),
                        randint(0, 40),
                        randint(10, 30),
                        randint(5, 10),
                    ]
                )

                if alpha == user1:
                    user2_hp -= damage
                    hpover = 0 if user2_hp < 0 else user2_hp
                else:
                    user1_hp -= damage
                    hpover = 0 if user1_hp < 0 else user1_hp

                randommsg = choice(
                    [
                        f"**{alpha.name}** deals **{damage}** damage with an OP punch.\n**{beta.name}** is left with {hpover} HP",
                        f"**{alpha.name}** lands an amazing punch on **{beta.name}** dealing **{damage}** damage!\n**{beta.name}** is left over with {hpover} HP!",
                        f"**{alpha.name}** lands a dangerous punch on **{beta.name}** dealing **{damage}** damage!\n**{beta.name}** is left over with {hpover} HP!",
                    ]
                )
                await ctx.send(f"{randommsg}")

            elif msg.content.lower() == "kick":
                damage = choice(
                    [
                        randint(30, 45),
                        randint(30, 60),
                        randint(-50, -1),
                        randint(-40, -1),
                    ]
                )
                if damage > 0:

                    if alpha == user1:
                        user2_hp -= damage
                        hpover = 0 if user2_hp < 0 else user2_hp
                    else:
                        user1_hp -= damage
                        hpover = 0 if user1_hp < 0 else user1_hp

                    await ctx.send(
                        choice(
                            [
                                f"**{alpha.name}** kicks **{beta.name}** and deals **{damage}** damage\n**{beta.name}** is left over with **{hpover}** HP",
                                f"**{alpha.name}** lands a dank kick on **{beta.name}**, dealing **{damage}** damage.\n**{beta.name}** is left over with **{hpover}** HP",
                            ]
                        )
                    )
                elif damage < 0:

                    if alpha == user1:
                        user1_hp += damage
                        hpover = 0 if user1_hp < 0 else user1_hp
                    else:
                        user2_hp += damage
                        hpover = 0 if user2_hp < 0 else user2_hp

                    await ctx.send(
                        choice(
                            [
                                f"**{alpha.name}** flipped over while kicking their opponent, dealing **{-damage}** damage to themselves.",
                                f"{alpha.name} tried to kick {beta.name} but FELL DOWN! They took {-damage} damage!",
                            ]
                        )
                    )

            elif msg.content.lower() == "slap":
                damage = choice(
                    [
                        randint(20, 60),
                        randint(0, 50),
                        randint(30, 70),
                        randint(0, 40),
                        randint(10, 30),
                        randint(5, 10),
                    ]
                )

                if alpha == user1:
                    user2_hp -= damage
                    hpover = 0 if user2_hp < 0 else user2_hp
                else:
                    user1_hp -= damage
                    hpover = 0 if user1_hp < 0 else user1_hp

                await ctx.send(
                    f"**{alpha.name}** slaps their opponent, and deals **{damage}** damage.\n{beta.name} is left over with **{hpover}** HP"
                )

            elif msg.content.lower() == "end":
                await ctx.send(f"{alpha.name} ended the game. What a pussy.")
                return

            elif (
                    msg.content.lower() != "kick"
                    and msg.content.lower() != "slap"
                    and msg.content.lower() != "punch"
                    and msg.content.lower() != "end"
            ):
                if fails_user1 >= 1 or fails_user2 >= 1:
                    return await ctx.send(
                        "This game has ended due to multiple invalid choices. God ur dumb"
                    )
                if alpha == user1:
                    fails_user1 += 1
                else:
                    fails_user2 += 1
                await ctx.send("That is not a valid choice!")
                x -= 1

            x += 1

    @commands.command(brief="Let me tell a joke!")
    async def joke(self, ctx):
        """
        Returns a random joke from https://official-joke-api.appspot.com/jokes/
        """
        res = await self.bot.session.get("https://official-joke-api.appspot.com/jokes/random")
        data = await res.json()
        await ctx.invis(f'{data["setup"]}\n||{data["punchline"]}||')

    @commands.command()
    async def urban(self, ctx, *, term: str):
        """
        Searches a term on urban dictionary and sends the result.
        """
        res = await ctx.session.get('http://api.urbandictionary.com/v0/define', params={'term': term})
        if not res.ok:
            await ctx.send(f'An error occured at the API. Try again with a different word or wait a bit.')
            return

        data = await res.json()
        if not data['list']:
            await ctx.send(f'No results were found for term `{term}`. Try again with a different word.')
            return

        menu = MenuPages(source=UrbanSource(data['list']), timeout=30, delete_message_after=True)
        await menu.start(ctx)

    @commands.command(aliases=["dankmemes"], brief="Shows a meme from reddit")
    @commands.cooldown(1, 1.5, type=BucketType.user)
    async def dankmeme(self, ctx):
        """Shows a meme from r/dankmemes."""
        res = await ctx.session.get("https://www.reddit.com/r/dankmemes/random/.json")
        data = await res.json()
        image = data[0]["data"]["children"][0]["data"]["url"]
        permalink = data[0]["data"]["children"][0]["data"]["permalink"]
        url = f"https://reddit.com{permalink}"
        title = data[0]["data"]["children"][0]["data"]["title"]
        ups = data[0]["data"]["children"][0]["data"]["ups"]
        # downs = data[0]["data"]["children"][0]["data"]["downs"]
        comments = data[0]["data"]["children"][0]["data"]["num_comments"]

        em = Embed(colour=discord.Color.blurple(), title=title, url=url)
        em.set_image(url=image)
        em.description = f"<:UpVote:878877980003270686> {ups} <:comment:882798531121913857> {comments}"

        await ctx.send(embed=em)

    @commands.command(aliases=["noticemesenpai"])
    async def noticeme(self, ctx):
        """ Notice me senpai! owo """
        await ctx.send(embed=discord.Embed(color=0xff6d7a).set_image(url='https://i.alexflipnote.dev/500ce4.gif'))

    @commands.command(aliases=["slots", "bet"])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def slot(self, ctx):
        """ Roll the slot machine """
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = choice(emojis)
        b = choice(emojis)
        c = choice(emojis)

        slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if a == b == c:
            await ctx.send(f"{slotmachine} All matching, you won! 🎉")
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f"{slotmachine} 2 in a row, you won! 🎉")
        else:
            await ctx.send(f"{slotmachine} No match, you lost 😢")


def setup(bot):
    bot.add_cog(Fun(bot))
