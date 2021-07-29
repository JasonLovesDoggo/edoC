from discord.ext.commands import CommandInvokeError

import discord
import requests
from discord.ext import commands
import aiohttp

from utils import default
from utils.vars import *


class Skyblock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.lvl50 = 55172425
        self.lvl51 = 59472425
        self.lvl52 = 64072425
        self.lvl53 = 68972425
        self.lvl54 = 74172425
        self.lvl55 = 79672425
        self.lvl56 = 85472425
        self.lvl57 = 91572425
        self.lvl58 = 97972425
        self.lvl59 = 104672425
        self.lvl60 = 111672425
        self.runecraftingCap = 75400
        self.separator = '{:,}'

    @commands.command()
    async def taming(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

                for profile in data["profiles"].values():
                    if pname is None:
                        if profile['current']:
                            target_profile = profile
                            pname = profile['cute_name']
                            break
                    elif pname.lower() == profile['cute_name'].lower():
                        target_profile = profile
                        pname = profile['cute_name']
                        break
                if target_profile is None:
                    raise CommandInvokeError

                print(
                    f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Taming stats.")

                xpForMax = target_profile['data']['levels']['taming']['xp']
                of = self.lvl50 - xpForMax

                if of <= 0:
                    of = 0

                xpForNext = target_profile['data']['levels']['taming']['xpForNext']
                if xpForNext is None or xpForNext <= 0:
                    xpForNext = 0

                xpNow = target_profile['data']['levels']['taming']['xpCurrent']
                xpMax = xpForNext - xpNow
                if xpMax <= 0:
                    xpMax = 0

                embed = discord.Embed(
                    title='Taming Level for ' + nameApi['name'] + ' On Profile ' + pname,
                    url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
                    description='**Total Taming EXP: ** ' + self.separator.format(round(int(xpForMax))),
                    color=discord.Colour.from_rgb(137, 207, 240)
                )

                # Contents of discord embed
                embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
                embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
                embed.set_footer(text=embedfooter)
                embed.timestamp = ctx.message.created_at

                embed.add_field(name='**Taming Level**',
                                value=(str(round(target_profile['data']['levels']['taming']['level']))) + '/ 50')
                embed.add_field(name='**Level with Progress**',
                                value=(round(target_profile['data']['levels']['taming']['levelWithProgress'], 2)))
                embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                                inline=False)
                embed.add_field(name='**Ranking**',
                                value=self.separator.format(int(target_profile['data']['levels']['taming']['rank'])))
                embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

                await ctx.send(embed=embed)

    @commands.command()
    async def farming(self, ctx, name, pname=None):
        separator = '{:,}'
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        levelCap = target_profile['data']['level_caps']['farming']
        xpCap = 0
        if levelCap == 50:
            xpCap = self.lvl50
        elif levelCap == 51:
            xpCap = self.lvl51
        elif levelCap == 52:
            xpCap = self.lvl52
        elif levelCap == 53:
            xpCap = self.lvl53
        elif levelCap == 54:
            xpCap = self.lvl54
        elif levelCap == 55:
            xpCap = self.lvl55
        elif levelCap == 56:
            xpCap = self.lvl56
        elif levelCap == 57:
            xpCap = self.lvl57
        elif levelCap == 58:
            xpCap = self.lvl58
        elif levelCap == 59:
            xpCap = self.lvl59
        elif levelCap == 60:
            xpCap = self.lvl60

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Farming stats.")

        xpForMax = target_profile['data']['levels']['farming']['xp']
        farmingCap = 111672425
        of = farmingCap - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['farming']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['farming']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        # Start of the embed
        embed = discord.Embed(
            title='Farming Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Farming EXP: ** ' + separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(240, 240, 236)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Level Cap**', value=str(round(levelCap)))
        embed.add_field(name='**Farming Level**',
                        value=(str(round(target_profile['data']['levels']['farming']['level']))) + '/' + (
                            str(round(target_profile['data']['levels']['farming']['maxLevel']))))

        if levelCap == 60:
            embed.add_field(name=f'**XP Over Level {levelCap}**',
                            value=(separator.format(round(xpForMax - xpCap)) + ' Overflow XP'))
            embed.add_field(name='**Ranking**',
                            value=separator.format(target_profile['data']['levels']['farming']['rank']))
            embed.add_field(name='**Level with Progress**',
                            value=(round(target_profile['data']['levels']['farming']['levelWithProgress'], 2)))

            await ctx.send(embed=embed)
        else:
            embed.add_field(name=f'**Level Required to Level {levelCap}**',
                            value=separator.format(round(xpCap - xpForMax)))
            embed.add_field(name='**Remaining XP for Next Level**', value=separator.format(round(int(xpMax))),
                            inline=False)
            embed.add_field(name='**Ranking**',
                            value=separator.format(target_profile['data']['levels']['farming']['rank']))
            embed.add_field(name='**Xp Required for Max Level**', value=separator.format(round(int(of))))
            embed.add_field(name='**Level with Progress**',
                            value=(round(target_profile['data']['levels']['farming']['levelWithProgress'], 2)))

            await ctx.send(embed=embed)

    @commands.command()
    async def mining(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Mining stats.")

        xpForMax = target_profile['data']['levels']['mining']['xp']
        of = self.lvl60 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['mining']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['mining']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        # Start of the embed
        embed = discord.Embed(
            title='Mining Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Mining EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=green
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Mining Level**',
                        value=(str(round(target_profile['data']['levels']['mining']['level']))) + '/ 60')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['mining']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['mining']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command()
    async def combat(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Combat stats.")

        xpForMax = target_profile['data']['levels']['combat']['xp']
        of = self.lvl60 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['combat']['xpForNext']
        if xpForNext == None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['combat']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Combat Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Combat EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(212, 175, 55)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Combat Level**',
                        value=(str(round(target_profile['data']['levels']['combat']['level']))) + '/ 60')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['combat']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['combat']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command(name='foraging')
    async def foraging(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Foraging stats.")

        xpForMax = target_profile['data']['levels']['foraging']['xp']
        of = self.lvl50 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['foraging']['xpForNext']
        if xpForNext == None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['foraging']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Foraging Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Foraging EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(0, 100, 0)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Foraging Level**',
                        value=(str(round(target_profile['data']['levels']['foraging']['level']))) + '/ 50')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['foraging']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['foraging']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command()
    async def fishing(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Fishing stats.")

        xpForMax = target_profile['data']['levels']['fishing']['xp']
        of = self.lvl50 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['fishing']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['fishing']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Fishing Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Fishing EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(27, 149, 224)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Fishing Level**',
                        value=(str(round(target_profile['data']['levels']['fishing']['level']))) + '/ 50')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['fishing']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['fishing']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command(name='enchanting')
    async def enchanting(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Enchanting stats.")

        xpForMax = target_profile['data']['levels']['enchanting']['xp']
        of = self.lvl60 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['enchanting']['xpForNext']
        if xpForNext == None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['enchanting']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Enchanting Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Enchanting EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(175, 124, 172)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Enchanting Level**',
                        value=(str(round(target_profile['data']['levels']['enchanting']['level']))) + '/ 60')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['enchanting']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['enchanting']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command(name='alchemy')
    async def alchemy(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Alchemy stats.")

        xpForMax = target_profile['data']['levels']['alchemy']['xp']
        of = self.lvl50 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['alchemy']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['alchemy']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Alchemy Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Alchemy EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(221, 20, 61)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Alchemy Level**',
                        value=(str(round(target_profile['data']['levels']['alchemy']['level']))) + '/ 60')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['alchemy']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['alchemy']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command(name='carpentry')
    async def carpentry(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Carpentry stats.")

        xpForMax = target_profile['data']['levels']['carpentry']['xp']
        of = self.lvl50 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['carpentry']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['carpentry']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Carpentry Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Carpentry EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(198, 162, 126)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Carpentry Level**',
                        value=(str(round(target_profile['data']['levels']['carpentry']['level']))) + '/ 50')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['carpentry']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['carpentry']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command(name='runecrafting')
    async def runecrafting(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Runecrafting stats.")

        xpForMax = target_profile['data']['levels']['runecrafting']['xp']
        of = self.runecraftingCap - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['runecrafting']['xpForNext']
        if xpForNext == None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['runecrafting']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Runecrafting Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Runecrafting EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=discord.Colour.from_rgb(255, 182, 193)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Runecrafting Level**',
                        value=(str(round(target_profile['data']['levels']['runecrafting']['level']))) + '/ 25')
        embed.add_field(name='**Level with Progress**',
                        value=(round(target_profile['data']['levels']['runecrafting']['levelWithProgress'], 2)))
        embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                        inline=False)
        embed.add_field(name='**Ranking**',
                        value=self.separator.format(int(target_profile['data']['levels']['runecrafting']['rank'])))
        embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))

        await ctx.send(embed=embed)

    @commands.command(name='dungeons', aliases=['dungeon', 'catacombs', 'cata'])
    async def dungeons(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Dungeons stats.")

        embed = discord.Embed(
            title='Dungeon Stats For ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Dungeon EXP:** ' + (
                str(round(target_profile['data']['dungeons']['catacombs']['level']['xp'], 2))),

        )
        embed.set_author(name='Made by StickyRunnerTR#9676')
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=f'Requested by {ctx.message.author}.')
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Catacombs Level**',
                        value=str(target_profile['data']['dungeons']['catacombs']['level']['level']))
        embed.add_field(name='**EXP Until Next Level**', value=str(
            target_profile['data']['dungeons']['catacombs']['level']['xpForNext'] -
            target_profile['data']['dungeons']['catacombs']['level']['xpCurrent']))
        embed.add_field(name='**Highest Floor In Catacombs**',
                        value=str(target_profile['data']['dungeons']['catacombs']['highest_floor']).replace('_',
                                                                                                            ' ').replace(
                            'f', 'F'), inline=False)
        if target_profile['data']['dungeons']['master_catacombs']['visited']:
            embed.add_field(name='**Highest Floor In Master Mode**',
                            value=str(target_profile['data']['dungeons']['master_catacombs']['highest_floor']).replace(
                                '_', ' ').replace('floor', 'Master'), inline=False)
        embed.add_field(name='**Healer**', value='Level: ' + str(
            target_profile['data']['dungeons']['classes']['healer']['experience']['level']))
        embed.add_field(name='**Mage**', value='Level: ' + str(
            target_profile['data']['dungeons']['classes']['mage']['experience']['level']))
        embed.add_field(name='**Tank**', value='Level: ' + str(
            target_profile['data']['dungeons']['classes']['tank']['experience']['level']))
        embed.add_field(name='**Berserk**', value='Level: ' + str(
            target_profile['data']['dungeons']['classes']['berserk']['experience']['level']))
        embed.add_field(name='**Archer**', value='Level: ' + str(
            target_profile['data']['dungeons']['classes']['archer']['experience']['level']))

        await ctx.send(embed=embed)

    @commands.command(aliases=['slayer'])
    async def slayers(self, ctx, name, pname=None):
        nameApi = requests.get('https://api.mojang.com/users/profiles/minecraft/' + name).json()
        target_profile = None

        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sky.shiiyu.moe/api/v2/profile/' + name) as api:
                data = await api.json()

        for profile in data["profiles"].values():
            if pname is None:
                if profile['current']:
                    target_profile = profile
                    pname = profile['cute_name']
                    break
            elif pname.lower() == profile['cute_name'].lower():
                target_profile = profile
                pname = profile['cute_name']
                break
        if target_profile is None:
            raise CommandInvokeError

        t1eman = target_profile['data']['slayers']['enderman']['kills']['1'] if '1' in \
                                                                                target_profile['data']['slayers'][
                                                                                    'enderman']['kills'] else 0
        t2eman = target_profile['data']['slayers']['enderman']['kills']['2'] if '2' in \
                                                                                target_profile['data']['slayers'][
                                                                                    'enderman']['kills'] else 0
        t3eman = target_profile['data']['slayers']['enderman']['kills']['3'] if '3' in \
                                                                                target_profile['data']['slayers'][
                                                                                    'enderman']['kills'] else 0
        t4eman = target_profile['data']['slayers']['enderman']['kills']['4'] if '4' in \
                                                                                target_profile['data']['slayers'][
                                                                                    'enderman']['kills'] else 0

        t1sven = target_profile['data']['slayers']['wolf']['kills']['1'] if '1' in \
                                                                            target_profile['data']['slayers']['wolf'][
                                                                                'kills'] else 0
        t2sven = target_profile['data']['slayers']['wolf']['kills']['2'] if '2' in \
                                                                            target_profile['data']['slayers']['wolf'][
                                                                                'kills'] else 0
        t3sven = target_profile['data']['slayers']['wolf']['kills']['3'] if '3' in \
                                                                            target_profile['data']['slayers']['wolf'][
                                                                                'kills'] else 0
        t4sven = target_profile['data']['slayers']['wolf']['kills']['4'] if '4' in \
                                                                            target_profile['data']['slayers']['wolf'][
                                                                                'kills'] else 0

        t1tara = target_profile['data']['slayers']['spider']['kills']['1'] if '1' in target_profile['data']['slayers'][
            'spider']['kills'] else 0
        t2tara = target_profile['data']['slayers']['spider']['kills']['2'] if '2' in target_profile['data']['slayers'][
            'spider']['kills'] else 0
        t3tara = target_profile['data']['slayers']['spider']['kills']['3'] if '3' in target_profile['data']['slayers'][
            'spider']['kills'] else 0
        t4tara = target_profile['data']['slayers']['spider']['kills']['4'] if '4' in target_profile['data']['slayers'][
            'spider']['kills'] else 0

        t1reve = target_profile['data']['slayers']['zombie']['kills']['1'] if '1' in target_profile['data']['slayers'][
            'zombie']['kills'] else 0
        t2reve = target_profile['data']['slayers']['zombie']['kills']['2'] if '2' in target_profile['data']['slayers'][
            'zombie']['kills'] else 0
        t3reve = target_profile['data']['slayers']['zombie']['kills']['3'] if '3' in target_profile['data']['slayers'][
            'zombie']['kills'] else 0
        t4reve = target_profile['data']['slayers']['zombie']['kills']['4'] if '4' in target_profile['data']['slayers'][
            'zombie']['kills'] else 0
        t5reve = target_profile['data']['slayers']['zombie']['kills']['5'] if '5' in target_profile['data']['slayers'][
            'zombie']['kills'] else 0

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Slayers stats.")

        embed = discord.Embed(
            title='Slayer Information for ' + nameApi['name'],
            url=f'https://sky.shiiyu.moe/stats/{name}/{pname}',
            description='**Total Slayer EXP:** ' + self.separator.format(int(target_profile['data'][
                                                                                 'slayer_xp'])) + 'XP' + '\n ***Total Coins Spent on Slayers: ***' + self.separator.format(
                int(target_profile['data']['slayer_coins_spent']['total'])) + ' coins',
            color=discord.Colour.from_rgb(153, 0, 0)
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://mc-heads.net/head/' + name)
        embed.set_footer(text=embedfooter)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Revenent Horror \nLevel**',
                        value='Level ' + str(target_profile['data']['slayers']['zombie']['level']['currentLevel']))
        embed.add_field(name='**Revenant Horror \nGathered XP**',
                        value=str(
                            self.separator.format(target_profile['data']['slayers']['zombie']['level']['xp'])) + 'XP')
        embed.add_field(name='**Coins Spent on \nRevenant Slayer**',
                        value=self.separator.format(
                            int(target_profile['data']['slayer_coins_spent']['zombie'])) + ' Coins')
        embed.add_field(name='Revenant Horror Kills:',
                        value='```prolog\nT1: ' + str(t1reve) + '\nT2: ' + str(t2reve) + '\nT3: ' + str(
                            t3reve) + '\nT4: ' + str(t4reve) + '\nT5: ' + str(t5reve) + '```', inline=False)

        embed.add_field(name='**Tarantula Broodfather \nLevel**',
                        value='Level ' + str(target_profile['data']['slayers']['spider']['level']['currentLevel']))
        embed.add_field(name='**Tarantula Broodfatherr \nGathered XP**',
                        value=str(
                            self.separator.format(target_profile['data']['slayers']['spider']['level']['xp'])) + 'XP')
        embed.add_field(name='**Coins Spent on \nTarantula Slayer**',
                        value=self.separator.format(
                            int(target_profile['data']['slayer_coins_spent']['spider'])) + ' Coins')
        embed.add_field(name='Tarantula Broodfather Kills:',
                        value='```prolog\nT1: ' + str(t1tara) + '\nT2: ' + str(t2tara) + '\nT3: ' + str(
                            t3tara) + '\nT4: ' + str(t4tara) + '```', inline=False)

        embed.add_field(name='**Sven Packmaster \nLevel**',
                        value='Level ' + str(target_profile['data']['slayers']['wolf']['level']['currentLevel']))
        embed.add_field(name='**Sven Packmaster \nGathered XP**',
                        value=str(
                            self.separator.format(target_profile['data']['slayers']['wolf']['level']['xp'])) + 'XP')
        embed.add_field(name='**Coins Spents on \nSven Slayer**',
                        value=self.separator.format(
                            int(target_profile['data']['slayer_coins_spent']['wolf'])) + ' Coins')
        embed.add_field(name='Sven Packmaster Kills:',
                        value='```prolog\nT1: ' + str(t1sven) + '\nT2: ' + str(t2sven) + '\nT3: ' + str(
                            t3sven) + '\nT4: ' + str(t4sven) + '```', inline=False)

        embed.add_field(name='**Voidgloom Seraph \nLevel**',
                        value='Level ' + str(target_profile['data']['slayers']['enderman']['level']['currentLevel']))
        embed.add_field(name='**Voidgloom Seraph \nGathered XP**', value=str(
            self.separator.format(target_profile['data']['slayers']['enderman']['level']['xp'])) + 'XP')
        embed.add_field(name='**Coins Spent on \nVoidgloom Slayer**', value=self.separator.format(
            int(target_profile['data']['slayer_coins_spent']['enderman'])) + ' Coins')
        embed.add_field(name='Voidgloom Seraph Kills:',
                        value='```prolog\nT1: ' + str(t1eman) + '\nT2: ' + str(t2eman) + '\nT3: ' + str(
                            t3eman) + '\nT4: ' + str(t4eman) + '```', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="helpme")
    async def helpme(ctx):
        embed = discord.Embed(
            title="**How to Use:**",
            description="req <desired skill> <player name> <profile name> (Proflie name is not required.)",
            color=discord.Colour.from_rgb(255, 255, 255)
        )
        embed.set_footer(text='With the helps of VxnomRandom#6495, Cow#1336 and EzDzQzR#5493.')

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title='**Error!**',
                description=f'The command you have requested is not working. \nPlease use one of these skills right or make sure you have typed one of these:\ntaming, farming, mining, combat, foraging, fishing, enchanting, alchemy, carpentry, runecrafting, slayers, dungeons.',

                color=discord.Colour.from_rgb(255, 0, 0)
            )
            embed.set_author(name='Made by StickyRunnerTR#9676')
            embed.set_footer(text=f'Requested by {ctx.message.author}.')
            embed.set_footer(text='With the helps of VxnomRandom#6495, Cow#1336 and EzDzQzR#5493.')
            embed.timestamp = ctx.message.created_at

            await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title='**Error!**',
                description=f'The command you have requested is not working. \nMake sure you have typed the player name right, or make sure your Skill API is on.',
                color=discord.Colour.from_rgb(255, 0, 0)
            )

            embed.set_author(name='Made by StickyRunnerTR#9676')
            embed.set_footer(text=f'Requested by {ctx.message.author}.')
            embed.timestamp = ctx.message.created_at
            embed.set_footer(text='With the helps of VxnomRandom#6495, Cow#1336 and EzDzQzR#5493.')

            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='**Error!**',
                description=f'The command you have requested is not working. \nMake sure you have typed required arguments.',
                color=discord.Colour.from_rgb(255, 0, 0)
            )

            embed.set_author(name='Made by StickyRunnerTR#9676')
            embed.set_footer(text=f'Requested by {ctx.message.author}.')
            embed.set_footer(text='With the helps of VxnomRandom#6495, Cow#1336 and EzDzQzR#5493.')
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)

        else:
            print('Unknown error!')
        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] made an error typing a command. The error is unknown!")


def setup(bot):
    bot.add_cog(Skyblock(bot))
