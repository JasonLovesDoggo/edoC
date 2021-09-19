# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import random as rng
from io import BytesIO
from os import listdir

import discord
from aiohttp import ClientConnectorError, ContentTypeError
from discord import Embed, File  # , Option
from discord.ext.commands import *

from utils.checks import UrlSafe, MemberConver
from utils.http import get
from utils.vars import *


class Invalid_endpoint(BaseException):
    pass


class Image(Cog, description='Image Related commands are here'):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.logschannel = self.bot.get_channel(self.config["edoc_logs"])
        self.dogphotospath = listdir("C:/Users/Jason/edoC/data/img/Dog Picks")

        # @bot.slash_command(guild_ids=[819282410213605406], aliases=['blurify', 'makeblury'], brief='outputs the members pfp blury')
        # async def blur(ctx,
        #               comment: Option(str, "Enter The Message"),
        #               member: MemberConver,
        #               username: Option(str, "Choose The Username", required=False)
        #               ):
        #    member = member or await authorOrReferenced(ctx)
        #    username = username or ctx.author.display_name
        #    async with self.bot.session.get(
        #            f'https://some-random-api.ml/canvas/youtube-comment?avatar{member.avatar.url}&username={username}&comment={comment}'
        #    ) as af:
        #        if 300 > af.status >= 200:
        #            fp = BytesIO(await af.read())
        #            file = discord.File(fp, "blury.png")
        #            em = discord.Embed(color=invis).set_image(url="attachment://blury.png")
        #            await ctx.send(embed=em, file=file)
        #        else:
        #            await ctx.send('The blurification procsess must have stopped working :(')

    # TODO swap custom alexflipnote 'wrapper' to the more official one
    def check_endpoint(self, endpoints: list, endpoint, type):
        endpoint = endpoint.lower()
        if endpoint not in endpoints:
            raise Invalid_endpoint(
                f'{endpoint} isnt an valid endpoint\nthe list of valid {type} ones are {endpoints}')

    async def get_r_animal(self, ctx, endpoint: str):
        availible_endpoints = ['panda', 'dog', 'cat', 'fox', 'red_panda', 'koala',
                               'birb', 'raccoon', 'kangaroo', 'whale']
        self.check_endpoint(availible_endpoints, endpoint, 'animal')
        async with ctx.session.get(f"https://some-random-api.ml/animal/{endpoint}") as r:
            if r.status != 429:
                content = await r.json()
            else:
                return await ctx.error('Too many requests, please try again later.')
        e = Embed(color=invis)
        e.set_footer(text=content['fact'])
        e.set_image(url=content['image'])
        await ctx.try_reply(embed=e)

    async def editpfp(self, ctx, member, endpoint):
        availible_endpoints = ['gay', 'glass', 'wasted', 'passed', 'jail', 'comrade']
        self.check_endpoint(availible_endpoints, endpoint, 'pfp')
        avatar = member.avatar.url

        img = f'https://some-random-api.ml/canvas/{endpoint}?avatar={avatar}'
        e = Embed(color=invis)
        e.set_image(url=img)
        await ctx.try_reply(embed=e)

    async def alexflipnote(self, ctx, url: str, endpoint: str, token: str = None):
        try:
            r = await get(
                url, res_method="json", no_cache=True,
                headers={"Authorization": token} if token else None
            )
        except ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")
        await ctx.send(r[endpoint])

    @command(aliases=['howgay', 'gay'], brief="Rates your gayness")
    async def gayrate(self, ctx, member: MemberConver = None):
        """Rate your gayness or another users gayness. 1-100% is returned"""
        await ctx.trigger_typing()
        user = member.name + " is" if member else "You are"
        gaynes = f'{int(str(abs(hash(user)))[:2]):.2f}'
        avatar = member.avatar.url
        img = f'https://some-random-api.ml/canvas/gay?avatar={avatar}'
        emb = Embed(
            title="gay r8 machine",
            description=f"{user} **{gaynes}%** gay \U0001f308",
            color=discord.Color.random(),
        ).set_thumbnail(url=img)
        await ctx.send(embed=emb)

    @gayrate.error
    async def gayrate_error(self, ctx, error):
        if isinstance(error, MemberNotFound):
            gaynes = f'{int(str(abs(hash(error.argument)))[:2]):.2f}'
            emb = Embed(
                title="gay r8 machine",
                description=f"{error.argument} is **{gaynes} \U0001f308",
                color=discord.Color.random(),
            )
            await ctx.send(embed=emb)
        else:
            raise error

    @group(aliases=['profilepic'], brief='Modify a pfp')
    async def pfp(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @group(aliases=['cate', 'kat', 'kate', 'catoo'], brief='Gives you a random cat.')
    @cooldown(2, 6, type=BucketType.user)
    async def cat(self, ctx):
        base_url = 'https://cataas.com'
        async with ctx.session.get(f'{base_url}/cat?json=true') as resp:
            if resp.status != 200:
                return await ctx.send('No cat found :(')
            js = await resp.json()
            feet = str(js['tags']).replace('[', '').replace(']', '').replace('\'', '')
            await ctx.send(embed=discord.Embed().set_image(
                url=base_url + js['url']).set_footer(text=f'Tags: {feet}' if len(feet) > 1 else ''))

    @cat.command(aliases=['says'])
    async def say(self, ctx, word: UrlSafe, color='white'):
        url = f'https://cataas.com/cat/says/{word}?size=50&color={color}'
        await ctx.send(embed=discord.Embed(title='Cate', url=url).set_image(url=url))

    @command(aliases=['lizzyboi'])
    @cooldown(1, 2, type=BucketType.user)
    async def lizard(self, ctx):
        """Gives you a random Lizard pic."""
        async with ctx.session.get('https://nekos.life/api/v2/img/lizard') as api:
            data = await api.json()
        emb = discord.Embed(title="Lizard",
                            color=invis)
        emb.set_image(url=data['url'])
        await ctx.send(embed=emb)

    @command(aliases=["MyDoggo", "Bella", "Belz", "WhosAgudGurl"], brief='Posts a random pic of my doggo Bella :)')
    async def MyDog(self, ctx):
        imge = rng.choice(self.dogphotospath)  # change dir name to whatever
        file = discord.File(f"C:/Users/Jason/edoC/data/img/Dog Picks/{imge}")
        try:
            await ctx.send(file=file)
        except discord.HTTPException:
            await ctx.error(
                f"The file {imge} is too large this has been reported to the devs\ntry to run the cmd again")

    @command()
    async def supreme(self, ctx, *, text: str):
        embed = Embed(title=f"Rendered by {ctx.author.display_name} VIA {ctx.guild.me.display_name}",
                      color=invis).set_image(url="attachment://supreme.png")
        image = File(await (await self.bot.alex_api.supreme(text=text)).read(), "supreme.png")
        await ctx.send(embed=embed, file=image)

    @command(aliases=['horny'], brief='Horny license just for u')
    async def hornylicense(self, ctx, member: MemberConver = None):
        await ctx.trigger_typing()
        async with ctx.session.get(
                f'https://some-random-api.ml/canvas/horny?avatar={member.avatar.url}'
        ) as af:
            if 300 > af.status >= 200:
                fp = BytesIO(await af.read())
                file = discord.File(fp, "horny.png")
                em = discord.Embed(
                    title="Bonk!",
                    color=0xefa490,
                )
                em.set_image(url="attachment://horny.png")
                await ctx.send(embed=em, file=file)
            else:
                await ctx.error('No horny :(')

    @command(aliases=['simpid', 'simpcard'], brief='Simp id just for u')
    async def simp(self, ctx, member: MemberConver = None):
        await ctx.trigger_typing()
        async with ctx.session.get(
                f'https://some-random-api.ml/canvas/simpcard?avatar={member.avatar.url}'
        ) as af:
            if 300 > af.status >= 200:
                fp = BytesIO(await af.read())
                file = discord.File(fp, "simp.png")
                em = discord.Embed(
                    title="Bonk!",
                    color=0xefa490,
                )
                em.set_image(url="attachment://simp.png")
                await ctx.send(embed=em, file=file)
            else:
                await ctx.error('No simpy :(')

    @command(aliases=['pixelify', 'makepixely'], brief='outputs the members pfp pixelated')
    async def pixelate(self, ctx, member: MemberConver = None):
        await ctx.trigger_typing()
        async with ctx.session.get(
                f'https://some-random-api.ml/canvas/pixelate?avatar={member.avatar.url}'
        ) as af:
            if 300 > af.status >= 200:
                fp = BytesIO(await af.read())
                file = discord.File(fp, "pixels.png")
                em = discord.Embed(color=invis).set_image(url="attachment://pixels.png")
                await ctx.send(embed=em, file=file)
            else:
                await ctx.error('The pixel generator seems to be having a meltdown :(')

    @command(aliases=['blurify', 'makeblury'], brief='outputs the members pfp blury')
    async def blur(self, ctx, member: MemberConver = None):
        await ctx.trigger_typing()
        async with ctx.session.get(
                f'https://some-random-api.ml/canvas/blur?avatar={member.avatar.url}'
        ) as af:
            if 300 > af.status >= 200:
                fp = BytesIO(await af.read())
                file = discord.File(fp, "blury.png")
                em = discord.Embed(color=invis).set_image(url="attachment://blury.png")
                await ctx.send(embed=em, file=file)
            else:
                await ctx.error('The blurification procsess must have stopped working :(')

    @command()
    @cooldown(2, 6, type=BucketType.user)
    async def duck(self, ctx):
        """ Posts a random duck """
        await self.alexflipnote(ctx, "https://random-d.uk/api/v1/random", "url")

    @command()
    @cooldown(2, 6, type=BucketType.user)
    async def coffee(self, ctx):
        """ Posts a random coffee """
        await self.alexflipnote(ctx, "https://coffee.alexflipnote.dev/rng.json", "file")

    @command(brief='Gives you a random panda.')
    @cooldown(2, 6, BucketType.user)
    async def panda(self, ctx):
        await self.get_r_animal(ctx, 'panda')

    @command(brief='Gives you a random fox.')
    @cooldown(2, 6, BucketType.user)
    async def fox(self, ctx):
        await self.get_r_animal(ctx, 'fox')

    @command(brief='Gives you a random red panda.', aliases=['rpanda', 'redpand', 'red-panda', 'redpanda'])
    @cooldown(2, 6, BucketType.user)
    async def red_panda(self, ctx):
        await self.get_r_animal(ctx, 'red_panda')

    @command(brief='Gives you a random koala.')
    @cooldown(2, 6, BucketType.user)
    async def koala(self, ctx):
        await self.get_r_animal(ctx, 'koala')

    @command(brief='Gives you a random whale.')
    @cooldown(2, 6, BucketType.user)
    async def whale(self, ctx):
        async with ctx.session.get('https://some-random-api.ml/img/whale') as api:
            if api.status == 200:
                data = await api.json()
            else:
                return await ctx.error(f'Recieved a bad status code of {api.status}')
        emb = Embed(color=invis).set_image(url=data['link'])
        return await ctx.try_reply(embed=emb)

    @command(brief='Gives you a random kangaroo.', aliases=['kanga', 'karoo'])
    @cooldown(2, 6, BucketType.user)
    async def kangaroo(self, ctx):
        await self.get_r_animal(ctx, 'kangaroo')

    @command(brief='Gives you a random raccoon.')
    @cooldown(2, 6, BucketType.user)
    async def raccoon(self, ctx):
        await self.get_r_animal(ctx, 'raccoon')

    @command(brief='Gives you a random birb.', aliases=['bird', 'birbo'])
    @cooldown(2, 6, BucketType.user)
    async def birb(self, ctx):
        await self.get_r_animal(ctx, 'birb')

    @command(brief='Gives you a random dog.')
    @cooldown(2, 6, BucketType.user)
    async def dog(self, ctx):
        await self.get_r_animal(ctx, 'dog')

    @pfp.command(breif='Gayifies a pfp', name='gay')
    async def pfp_gay(self, ctx, member: MemberConver):
        await self.editpfp(ctx, member, 'gay')

    @pfp.command(breif='glassifies a pfp', name='glass', aliases=['glassy'])
    async def pfp_glass(self, ctx, member: MemberConver):
        await self.editpfp(ctx, member, 'glass')

    @pfp.command(breif='makes a pfp wasted', name='wasted', aliases=['waste'])
    async def pfp_wasted(self, ctx, member: MemberConver):
        await self.editpfp(ctx, member, 'wasted')

    @pfp.command(breif='passes a pfp', name='passed', aliases=['pass'])
    async def pfp_passed(self, ctx, member: MemberConver):
        await self.editpfp(ctx, member, 'passed')

    @pfp.command(breif='jails a pfp', name='jail', aliases=['jailed'])
    async def pfp_jail(self, ctx, member: MemberConver):
        await self.editpfp(ctx, member, 'jail')

    @pfp.command(breif='comradifies a pfp', name='comrade')
    async def pfp_comrade(self, ctx, member: MemberConver):
        await self.editpfp(ctx, member, 'comrade')

    @pfp.command(name='triggered', aliases=['trig', 'triggers'], brief='sends a img of the dudes pfp triggered')
    async def pfp_triggered(self, ctx, member: MemberConver):
        avatar = member.avatar.url
        e = Embed(color=invis)
        e.set_image(url="attachment://triggered.gif")
        async with ctx.session.get(f'https://some-random-api.ml/canvas/triggered?avatar={avatar}') as trigImg:
            imageData = BytesIO(await trigImg.read())  # read the image/bytes
            await ctx.try_reply(embed=e, file=discord.File(imageData, 'triggered.gif'))


def setup(bot):
    bot.add_cog(Image(bot))
