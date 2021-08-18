import asyncio
import json
import os
import secrets
import sys
from io import BytesIO

import aiohttp
import nekos
from discord.ext import commands
from bs4 import BeautifulSoup
from jishaku.models import copy_context_with
from nekos import InvalidArgument

import discord
from utils import permissions, http, default
from utils.gets import getEmote
from utils.vars import *
import pyfiglet

dogphotospath = os.listdir("C:/Users/Jason/edoC/data/img/Dog Picks")

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.alex_api_token = self.config["alexflipnote_api"]
        self.DoggoPicsCount = len(os.listdir("C:/Users/Jason/edoC/data/img/Dog Picks"))
        self.logschannel = self.bot.get_channel(self.config["edoc_logs"])
        self.dogphotospath = dogphotospath

    @commands.command(aliases=["sayagain"])
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
        art = pyfiglet.figlet_format(f"{value}")
        await ctx.send(f"```\n{art}```")

    @commands.command(aliases=["roll", "dice"])
    async def rolldice(self, ctx, guess):
        answer = random.randint(1, 6)
        await ctx.reply(embed=discord.Embed(color={green if guess == answer else red},
                                            description=f"{'True' if guess == answer else 'False'} your guess was {guess} and the answer was {answer}"))

    @commands.command()
    async def rip(self, ctx, name: str = None, *, text: str = None):
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
            return await ErrorEmbed(ctx, error="Please keep your message under 25 chars")
        api = f'https://mcgen.herokuapp.com/a.php?i=2&h={a}&t={t}'
        emb = discord.Embed(color=random_color())
        emb.set_image(url=api)
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, aliases=['identify', 'captcha', 'whatis'])
    async def i(self, ctx, *, url: str):
        """Identify an image/gif using Microsofts Captionbot API"""
        with aiohttp.ClientSession() as session:
            async with session.post("https://www.captionbot.ai/api/message",
                                    data={"conversationId": "FPrBPK2gAJj", "waterMark": "", "userMessage": url}) as r:
                pass
        load = await self.get_json("https://www.captionbot.ai/api/message?waterMark=&conversationId=FPrBPK2gAJj")
        msg = '`{0}`'.format(json.loads(load)['BotMessages'][-1])
        await ctx.send(msg)


    @commands.command(aliases=["rfact", "rf"])
    @commands.cooldown(rate=1, per=1.3, type=commands.BucketType.user)
    async def RandomFact(self, ctx):
        fact = random.choice(random_facts)
        emb = discord.Embed(description=fact, color=random.choice(ColorsList))
        await ctx.reply(embed=emb, mention_author=False)

    async def randomimageapi(self, ctx, url: str, endpoint: str, token: str = None):
        try:
            r = await http.get(
                url, res_method="json", no_cache=True,
                headers={"Authorization": token} if token else None
            )
        except aiohttp.ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except aiohttp.ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")
        await ctx.send(r[endpoint])

    async def api_img_creator(self, ctx, url: str, filename: str, content: str = None):
        async with ctx.channel.typing():
            req = await http.get(url, res_method="read")

            if not req:
                return await ctx.send("I couldn't create the image ;-;")

            bio = BytesIO(req)
            bio.seek(0)
            await ctx.send(content=content, file=discord.File(bio, filename=filename))

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx):
        """ Posts a random duck """
        await self.randomimageapi(ctx, "https://random-d.uk/api/v1/random", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def coffee(self, ctx):
        """ Posts a random coffee """
        await self.randomimageapi(ctx, "https://coffee.alexflipnote.dev/random.json", "file")

    @commands.command(aliases=["doggo"])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dog(self, ctx):
        """ Posts a random dog """
        await self.randomimageapi(ctx, "https://random.dog/woof.json", "url")

    @commands.command(aliases=["cate", "kat"])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def cat(self, ctx):
        """ Posts a random cat """
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.thecatapi.com/v1/images/search?api_key={self.config['cat_key']}") as api:
                data = await api.json()
            emb = discord.Embed(title="Kate",
                                color=white)
            emb.set_image(url=data[0]["url"])
            await ctx.reply(embed=emb)

    @commands.command()
    @commands.cooldown(1, 2, type=commands.BucketType.user)
    async def lizard(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/lizard') as api:
                data = await api.json()
        emb = discord.Embed(title="Lizard",
                            color=green)
        emb.set_image(url=data['url'])
        await ctx.send(embed=emb)

    @commands.command(aliases=["MyDoggo", "Bella", "Belz", "WhosAgudGurl"])
    async def MyDog(self, ctx):
        img = random.choice(self.dogphotospath)  # change dir name to whatever
        file = discord.File(f"C:/Users/Jason/edoC/data/img/Dog Picks/{img}")
        try:
            await ctx.send(file=file)
        except discord.HTTPException:
            await ctx.send(
                f"The file that i was going to send was too large this has been reported to the devs\ntry to run the cmd again")
            await self.logschannel.send(f"{img} is too large to send <@&{self.config['dev_role']}>")

    @commands.command(aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        """ Coinflip! """
        coinsides = ["Heads", "Tails"]
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def topic(self, ctx):
        """ Generates a random topic to start a conversation up"""
        url = "https://www.conversationstarters.com/generator.php"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                output = await r.read()
                soup = BeautifulSoup(output, 'html5lib')
                topics = soup.find("div", {"id": "random"})
                topic = topics.contents[1]
        await ctx.send(f"**{topic}**")

    @commands.command(aliases=["ie"])
    async def iseven(self, ctx, num: int):
        """ checks if a number is even or not"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://api.isevenapi.xyz/api/iseven/{num}/') as api:
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

    @commands.command()
    async def clap(self, ctx, *, words: commands.clean_content = None):
        tosend = ""
        for word in words.split():
            tosend += f"👏 {word} "
        tosend += "👏"
        await ctx.reply(tosend)

    @commands.command(aliases=['Rcap'])
    async def Mock(self, ctx, *, words):
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
    @commands.check(permissions.is_owner)
    async def math(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @math.command(name="add", aliases=["addition"])
    async def math_add(self, ctx, num1: int, num2: int):
        answer = num1 + num2
        await ctx.send(answer)

    @math.command(name="sub", aliases=["subtraction"])
    async def math_sub(self, ctx, num1: int, num2: int):
        answer = num1 - num2
        await ctx.send(answer)

    @math.command(name="multi", aliases=["multiplication"])
    async def math_multi(self, ctx, num1: int, num2: int):
        answer = num1 * num2
        await ctx.send(answer)

    @math.command(name="division", aliases=["divide"])
    async def math_divide(self, ctx, num1: int, num2: int):
        answer = num1 // num2
        await ctx.send(answer)

    @commands.command(aliases=["JumboEmoji"])
    async def LargenEmoji(self, ctx, emoji):
        """Display your favorite emotes in large."""
        emote = getEmote(ctx, emoji)
        if emote:
            em = discord.Embed(colour=random_color())
            em.set_image(url=emote.url)
            await ctx.send(embed=em)
        else:
            await ctx.send(content='\N{HEAVY EXCLAMATION MARK SYMBOL} Only Emotes...')

    @commands.command()
    async def f(self, ctx, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    @commands.command()
    async def pick(self, ctx, one: str, two: str):
        """ picks between 2 things"""
        answer = random.choice([one, two])
        await ctx.send(f"**{answer}**")

    @commands.command()
    async def answer(self, ctx):
        """ purely just says yes or no randomly """
        ans = random.choice(["yes", "no"])
        await ctx.reply(ans)

    @commands.command(aliases=["uwuify", "makeuwu", "makeowo"])
    async def owoify(self, ctx, *, text: commands.clean_content = None):
        """ "owoifes" the text"""
        await ctx.reply(nekos.owoify(str(text)))

    @commands.command()
    async def why(self, ctx):
        """ why """
        await ctx.reply(nekos.why())

    @commands.command(hidden=True)
    @commands.check(permissions.is_taco)
    async def img(self, ctx, imgtype: str):
        try:
            await ctx.reply(nekos.img(target=imgtype))
        except InvalidArgument:
            await ctx.reply("Please put in the correct arguments ")

    @commands.command()
    async def test(self, ctx):
        """ Test command for testing """
        await ctx.send(f"**{ctx.author.name}** has done the **Test** command Oo")

    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def urban(self, ctx, *, search: commands.clean_content):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                url = await http.get(f"https://api.urbandictionary.com/v0/define?term={search}", res_method="json")
            except Exception:
                return await ctx.send("Urban API returned invalid data... might be down atm.")

            if not url:
                return await ctx.send("I think the API broke...")

            if not len(url["list"]):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(url["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            await ctx.send(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")

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
        await asyncio.sleep(.5)
        await message.edit(content="Backup 33% complete")
        await asyncio.sleep(.5)
        await message.edit(content="Backup 64% complete")
        await asyncio.sleep(.7)
        await message.edit(content="Backup 86% complete")
        await asyncio.sleep(.57)
        await message.edit(content="Backup 93% complete")
        await asyncio.sleep(2)
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
        await asyncio.sleep(.5)
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
        await ctx.author.send(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}")

    @commands.command()
    async def rate(self, ctx, *, thing: commands.clean_content):
        """ Rates what you desire """
        rate_amount = random.uniform(0.0, 100.0)
        await ctx.send(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @commands.command()
    async def ship(self, ctx, person1: commands, person2: commands):
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
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command(aliases=["howhot", "hot"])
    async def hotcalc(self, ctx, *, user: discord.Member = None):
        """ Returns a random percent for how hot is a discord user """
        user = user or ctx.author

        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        if hot > 25:
            emoji = "❤"
        elif hot > 50:
            emoji = "💖"
        elif hot > 75:
            emoji = "💞"
        else:
            emoji = "💔"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command(aliases=["howgay", "gay"])
    async def gaycalc(self, ctx, *, user: discord.Member = None):
        """ Returns a random percent for how gay is a discord user """
        user = user or ctx.author

        gay = random.randint(1, 100)

        await ctx.send(f"**{user.name}** is **{gay:.2f}%** gay :rainbow_flag: ")

    @commands.command(aliases=["noticemesenpai"])
    async def noticeme(self, ctx):
        """ Notice me senpai! owo """
        if not permissions.can_handle(ctx, "attach_files"):
            return await ctx.send("I cannot send images here ;-;")

        bio = BytesIO(await http.get("https://i.alexflipnote.dev/500ce4.gif", res_method="read"))
        await ctx.send(file=discord.File(bio, filename="noticeme.gif"))

    @commands.command(aliases=["slots", "bet"])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def slot(self, ctx):
        """ Roll the slot machine """
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if (a == b == c):
            await ctx.send(f"{slotmachine} All matching, you won! 🎉")
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f"{slotmachine} 2 in a row, you won! 🎉")
        else:
            await ctx.send(f"{slotmachine} No match, you lost 😢")


def setup(bot):
    bot.add_cog(Fun(bot))
