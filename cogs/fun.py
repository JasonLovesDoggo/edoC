# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import json
import random as rng
from asyncio import sleep
from collections import Counter
from io import BytesIO
from os import listdir
from secrets import token_urlsafe
from typing import Optional

import discord.ext.commands
from aiohttp import ClientConnectorError, ContentTypeError
from bs4 import BeautifulSoup
from discord.ext import commands
from nekos import InvalidArgument, why, owoify, img
from pyfiglet import figlet_format
from pyjokes import pyjokes

from cogs.discordinfo import plural
from utils.default import config, CustomTimetext
from utils.http import get
from utils.vars import *

dogphotospath = listdir("C:/Users/Jason/edoC/data/img/Dog Picks")


class Fun(commands.Cog, description='Fun and entertaining commands can be found below'):
    def __init__(self, bot):
        self.bot = bot
        self.config = config()
        self.alex_api_token = self.config["alexflipnote_api"]
        self.DoggoPicsCount = len(dogphotospath)
        self.logschannel = self.bot.get_channel(self.config["edoc_logs"])
        self.dogphotospath = dogphotospath

    async def alexflipnote(self, ctx, url: str, endpoint: str, token: str = None):
        try:
            r = await get(
                url, res_method="json", no_cache=True,
                headers={"Authorization": token} if token else None
            )
            r = await r.json()
        except ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")
        await ctx.send(r[endpoint])

    @commands.command()
    async def supreme(self, ctx, *, text: str):
        embed = discord.Embed(title=f"Rendered by {ctx.author.display_name} VIA {ctx.guild.me.display_name}", color=invis).set_image(url="attachment://supreme.png")
        image = discord.File(await (await self.bot.alex_api.supreme(text=text)).read(), "supreme.png")
        await ctx.send(embed=embed, file=image)


    @commands.command(aliases=["sayagain", 'repeat'])
    async def echo(self, ctx, *, what_to_say: commands.clean_content):
        """ repeats text """
        await ctx.reply(f'🦜 {what_to_say}')

    @commands.command(aliases=["8ball"])
    async def eightball(self, ctx, *, question: commands.clean_content):
        """ Consult 8ball to receive an answer """
        answer = random.choice(ballresponse)
        tosend = f"🎱 **Question:** {question}\n**Answer:** {answer}"
        emb = discord.Embed(description=tosend, color=random.choice(ColorsList))
        await ctx.reply(embed=emb)

    @commands.command(aliases=['asciiart'])
    async def ascii(self, ctx, *, value):
        """ sends ascii style art """
        art = figlet_format(f"{value}")
        try:
            await ctx.send(f"```\n{art}```")
        except Exception:
            await ctx.send('Thats a bit too long please try somthing shorter')

    @commands.command(aliases=["roll", "dice"])
    async def rolldice(self, ctx, guess):
        answer = random.randint(1, 6)
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
        await ctx.send(embed=emb)

    @commands.command(aliases=["rfact", "rf"])
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    async def RandomFact(self, ctx):
        """ Legit just posts a random fact"""
        fact = random.choice(random_facts)
        emb = discord.Embed(description=fact, color=random.choice(ColorsList))
        await ctx.reply(embed=emb, mention_author=False)
    async def api_img_creator(self, ctx, url: str, filename: str, content: str = None):
        async with ctx.channel.typing():
            req = await get(url, res_method="read")

            if not req:
                return await ctx.send("I couldn't create the image ;-;")

            bio = BytesIO(req)
            bio.seek(0)
            await ctx.send(content=content, file=discord.File(bio, filename=filename))

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx):
        """ Posts a random duck """
        await self.alexflipnote(ctx, "https://random-d.uk/api/v1/random", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def coffee(self, ctx):
        """ Posts a random coffee """
        await self.alexflipnote(ctx, "https://coffee.alexflipnote.dev/random.json", "file")

    # @commands.command(aliases=["doggo"])
    # @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    # async def dog(self, ctx):
    #    """ Posts a random dog """
    #    await self.randomimageapi(ctx, "https://random.dog/woof.json", "url")
    @commands.command()
    async def dog(self, ctx):
        """Gives you a random dog."""
        async with self.bot.session.get('https://random.dog/woof') as resp:
            if resp.status != 200:
                return await ctx.send('No dog found :(')

            filename = await resp.text()
            url = f'https://random.dog/{filename}'
            filesize = ctx.guild.filesize_limit if ctx.guild else 8388608
            if filename.endswith(('.mp4', '.webm')):
                async with ctx.typing():
                    async with self.bot.session.get(url) as other:
                        if other.status != 200:
                            return await ctx.send('Could not download dog video :(')

                        if int(other.headers['Content-Length']) >= filesize:
                            return await ctx.send(f'Video was too big to upload... See it here: {url} instead.')

                        fp = BytesIO(await other.read())
                        await ctx.send(file=discord.File(fp, filename=filename))
            else:
                await ctx.send(embed=discord.Embed(title='Random Dog').set_image(url=url))

    @commands.group(aliases=['cate', 'kat', 'kate', 'catoo'])
    @commands.cooldown(3, 7, type=commands.BucketType.user)
    async def cat(self, ctx):
        """Gives you a random cat."""
        if ctx.invoked_subcommand is not None:
            return
        base_url = 'https://cataas.com'
        async with ctx.session.get('https://cataas.com/cat?json=true') as resp:
            if resp.status != 200:
                return await ctx.send('No cat found :(')
            js = await resp.json()
            feet = str(js['tags']).replace('[', '').replace(']', '').replace('\'', '')
            await ctx.send(embed=discord.Embed(title='Meow!', url=base_url + js['url']).set_image(
                url=base_url + js['url']).set_footer(text=f'Tags: {feet}' if len(feet) > 1 else ''))

    @commands.command(aliases=['ac'])
    async def othercat(self, ctx):
        """Gives you a random cat."""
        async with ctx.session.get('https://api.thecatapi.com/v1/images/search') as resp:
            if resp.status != 200:
                return await ctx.send('No cat found :(')
            js = await resp.json()
            await ctx.send(embed=discord.Embed(title='Random Cat').set_image(url=js[0]['url']))

    @cat.command(aliases=['hello'])
    async def hi(self, ctx, color='white'):
        url = f'https://cataas.com/cat/says/hello?size=50&color={color}'
        await ctx.send(embed=discord.Embed(title='Hi!', url=url).set_image(url=url))

    @commands.command(aliases=['lizzyboi'])
    @commands.cooldown(1, 2, type=commands.BucketType.user)
    async def lizard(self, ctx):
        """Gives you a random Lizard pic."""
        async with self.bot.session.get('https://nekos.life/api/v2/img/lizard') as api:
            data = await api.json()
        emb = discord.Embed(title="Lizard",
                            color=green)
        emb.set_image(url=data['url'])
        await ctx.send(embed=emb)

    @commands.command(aliases=["MyDoggo", "Bella", "Belz", "WhosAgudGurl"])
    async def MyDog(self, ctx):
        """ Posts a random pic of my doggo Bella :) """
        imge = random.choice(self.dogphotospath)  # change dir name to whatever
        file = discord.File(f"C:/Users/Jason/edoC/data/img/Dog Picks/{imge}")
        try:
            await ctx.send(file=file)
        except discord.HTTPException:
            await ctx.send(
                f"The file that i was going to send was too large this has been reported to the devs\ntry to run the cmd again")
            await self.logschannel.send(f"{imge} is too large to send <@&{self.config['dev_role']}>")

    @commands.command(aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @commands.command(aliases=["flip", "coin"])
    async def coinflip(self, ctx, *, toss='Heads'):
        """ Coinflip! """
        responses = ['Heads', 'Tails']
        if len(toss) > 100:
            return await ErrorEmbed(ctx=ctx, err='Please keep the length of your toss down')
        value = random.randint(0, 0xffffff)
        embed = discord.Embed(

            colour=value,

        )
        embed.add_field(name=f'**User Side:** {toss}\n**Result:** {random.choice(responses)}',
                        value="Someone is gonna go cry to mommy.", inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=['Programmingjoke', 'pj'])
    async def ProgrammerHumor(self, ctx):
        """ Just run the command """
        joke = pyjokes.get_joke()
        await ctx.reply(joke)

    @commands.command(aliases=['renamedchuckJokes', 'gudjokesherenoscam', 'CJ'])
    async def ChuckJoke(self, ctx, person: commands.MemberConverter = 'Chuck Norris'):
        """ChuckNorris is the only man to ever defeat a brick wall in a game of tennis."""
        joke = random.choice(chuckjoke)
        nj = joke.replace('Chuck Norris', person)
        await ctx.reply(embed=discord.Embed(color=green, description=nj))

    @commands.command()
    async def ccjm(self, ctx):
        joke = random.choice(chuckjoke)
        nj = joke.replace('Chuck Norris', ctx.author.display_name)
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
        async with self.bot.session.get(f'https://api.isevenapi.xyz/api/iseven/{num}/') as api:
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

    @commands.command(alises=['randint', 'rn'])
    async def RandomNumber(self, ctx, minimum=0, maximum=100):
        """Displays a random number within an optional range.
        The minimum must be smaller than the maximum and the maximum number
        accepted is 1000.
        """

        maximum = min(maximum, 1000)
        if minimum >= maximum:
            await ctx.send('Maximum is smaller than minimum.')
            return

        await ctx.send(rng.randint(minimum, maximum))

    @commands.command(aliases=['random-lenny', 'rl'])
    async def rlenny(self, ctx):
        """Displays a random lenny face."""
        lenny = rng.choice([
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

        await ctx.send(rng.choice(choices))

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
        results = Counter(rng.choice(choices) for i in range(times))
        builder = []
        if len(results) > 15:
            builder.append('Only showing top 15 results...')
        for index, (elem, count) in enumerate(results.most_common(15), start=1):
            builder.append(f'{index}. {elem} ({plural(count):time}, {count / times:.2%})')
        data = '\n'.join(builder)
        data = BytesIO(data.encode("utf-8"))
        await ctx.send(file=discord.File(data, filename=f"{CustomTimetext('prolog', 'output')}"))

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
        if ctx.author == ctx.guild.owner or 511724576674414600:
            await ctx.message.delete()
        tosend = ""
        number = 1  # 1 if you want it to start with a capitol 0 if you want it to start with a lowercase
        for letter in words.lower():
            if number == 1:
                tosend += letter.upper()
                number = 0
            else:
                tosend += letter.lower()
                number = 1
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
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    @commands.command(aliases=['ans'])
    async def answer(self, ctx):
        """ purely just says yes or no randomly """
        ans = random.choice(["yes", "no"])
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

        if ctx.author == ctx.guild.owner or 511724576674414600:
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
        ship_amount = random.uniform(0.0, 100.0)
        if "jake" or "jason" or "edoc" in person1.lower() or person2.lower():
            ship_amount = 69.42069
        await ctx.send(f"`{person1}` and `{person2}` are **{round(ship_amount, 4)} compatible **")

    @commands.command()
    async def beer(self, ctx, user: discord.Member = None, *, reason: commands.clean_content = ""):
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
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command(aliases=["howhot", "hot"])
    async def hotcalc(self, ctx, *, user: discord.Member):
        """ Returns a random percent for how hot is a discord user """
        random.seed(user.id)
        r = random.randint(1, 100)
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

    @commands.command(aliases=["howgay", "gay"])
    async def gaycalc(self, ctx, *, user=None):
        """ Returns a random percent for how gay is a discord user """
        user = user or ctx.author
        gay = abs(hash(user))
        await ctx.send(f"**{user}** is **{int(str(gay)[:2]):.2f}%** gay :rainbow_flag: ")

    @commands.command(aliases=["noticemesenpai"])
    async def noticeme(self, ctx):
        """ Notice me senpai! owo """
        await ctx.send(embed=discord.Embed(color=0xff6d7a).set_image(url='https://i.alexflipnote.dev/500ce4.gif'))

    @commands.command(aliases=["slots", "bet"])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def slot(self, ctx):
        """ Roll the slot machine """
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if a == b == c:
            await ctx.send(f"{slotmachine} All matching, you won! 🎉")
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f"{slotmachine} 2 in a row, you won! 🎉")
        else:
            await ctx.send(f"{slotmachine} No match, you lost 😢")


def setup(bot):
    bot.add_cog(Fun(bot))
