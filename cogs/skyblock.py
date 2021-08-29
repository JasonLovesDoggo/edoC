# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import aiohttp
import requests
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError

from utils.vars import *

SbColors = {
    "ErrorColor": 0xff0000,
    "TamingColor": 0x89CFF0,
    "FishingColor": 0x1b95e0,
    "FarmingColor": 0xc3db79,
    "CombatColor": 0xd4af37,
    "ForagingColor": 0x006400,
    "EnchantingColor": 0xaf7cac,
    "RunecraftingColor": 0xffb6c1,
    "AlchemyColor": 0xdd143d,
    "CarpentryColor": 0xc6a27e,
    "MiningColor": 0x000000,
    "SlayersColor": 0x990000
}


class SkyblockUpdatedError(BaseException):
    pass

class Skyblock(commands.Cog, description='Skyblock cog for.. SKYBLOCK related commands'):
    def __init__(self, bot):
        self.bot = bot
        
        self.separator = '{:,}'
        self.target_profile = None
        self.MojangUrl = 'https://api.mojang.com/users/profiles/minecraft/'
        self.SkyV2 = 'https://sky.shiiyu.moe/api/v2/profile/'
        self.SkyShiiyuStats = 'https://sky.shiiyu.moe/stats/'
        self.McHeads = 'https://mc-heads.net/head/'

        self.TamingColor = SbColors["TamingColor"]
        self.FishingColor = SbColors["FishingColor"]
        self.FarmingColor = SbColors["FarmingColor"]
        self.CombatColor = SbColors["CombatColor"]
        self.ForagingColor = SbColors["ForagingColor"]
        self.EnchantingColor = SbColors["EnchantingColor"]
        self.RunecraftingColor = SbColors["RunecraftingColor"]
        self.AlchemyColor = SbColors["AlchemyColor"]
        self.CarpentryColor = SbColors["CarpentryColor"]
        self.MiningColor = SbColors["MiningColor"]
        self.SlayersColor = SbColors["SlayersColor"]

        # skills
        self.RuneCraftingCap = 75400
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

    """ SKILLS """

    @commands.command(name='taming', description='Shows your Taming statistics.')
    async def taming(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()
        async with ctx.session.get(self.SkyV2 + name) as api:
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
                url=f'{self.SkyShiiyuStats}{name}/{pname}',
                description='**Total Taming EXP: ** ' + self.separator.format(round(int(xpForMax))),
                color=self.TamingColor
            )
            # Contents of discord embed
            embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
            embed.set_thumbnail(url=self.McHeads + name)
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
    @commands.command(name='farming', description='Shows your Farming statistics.')
    async def farming(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
        if not target_profile:
            raise SkyblockUpdatedError

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
        of = self.lvl60 - xpForMax

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
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Farming EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.FarmingColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Level Cap**', value=str(round(levelCap)))
        embed.add_field(name='**Farming Level**',
                        value=(str(round(target_profile['data']['levels']['farming']['level']))) + '/' + (
                            str(round(target_profile['data']['levels']['farming']['maxLevel']))))

        if levelCap == 60:
            embed.add_field(name=f'**XP Over Level {levelCap}**',
                            value=(self.separator.format(round(xpForMax - xpCap)) + ' Overflow XP'))
            embed.add_field(name='**Ranking**',
                            value=self.separator.format(target_profile['data']['levels']['farming']['rank']))
            embed.add_field(name='**Level with Progress**',
                            value=(round(target_profile['data']['levels']['farming']['levelWithProgress'], 2)))

            await ctx.send(embed=embed)
        else:
            embed.add_field(name=f'**Level Required to Level {levelCap}**',
                            value=self.separator.format(round(xpCap - xpForMax)))
            embed.add_field(name='**Remaining XP for Next Level**', value=self.separator.format(round(int(xpMax))),
                            inline=False)
            embed.add_field(name='**Ranking**',
                            value=self.separator.format(target_profile['data']['levels']['farming']['rank']))
            embed.add_field(name='**Xp Required for Max Level**', value=self.separator.format(round(int(of))))
            embed.add_field(name='**Level with Progress**',
                            value=(round(target_profile['data']['levels']['farming']['levelWithProgress'], 2)))

            await ctx.send(embed=embed)

    @commands.command(name='mining', description='Shows your Mining statistics.')
    async def mining(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
        if not target_profile:
            raise SkyblockUpdatedError

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
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Mining EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.MiningColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)
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

    @commands.command(name='combat', description='Shows your Combat statistics.')
    async def combat(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            raise SkyblockUpdatedError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Combat stats.")

        xpForMax = target_profile['data']['levels']['combat']['xp']
        of = self.lvl60 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['combat']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['combat']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Combat Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Combat EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.CombatColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

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

    @commands.command(name='foraging', description='Shows your Foraging statistics.')
    async def foraging(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            raise SkyblockUpdatedError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Foraging stats.")

        xpForMax = target_profile['data']['levels']['foraging']['xp']
        of = self.lvl50 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['foraging']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['foraging']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Foraging Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Foraging EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.ForagingColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

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

    @commands.command(description='Shows your Fishing statistics.')
    async def fishing(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            raise SkyblockUpdatedError

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
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Fishing EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.FishingColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

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

    @commands.command(aliases=['ench'], description='Shows your Enchanting statistics.')
    async def enchanting(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            raise SkyblockUpdatedError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Enchanting stats.")

        xpForMax = target_profile['data']['levels']['enchanting']['xp']
        of = self.lvl60 - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['enchanting']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['enchanting']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Enchanting Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Enchanting EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.EnchantingColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

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

    @commands.command(aliases=['alch'], description='Shows your Alchemy statistics.')
    async def alchemy(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            raise SkyblockUpdatedError

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
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Alchemy EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.AlchemyColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

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

    @commands.command(name='carpentry', description='Shows your Carpentry statistics.')
    async def carpentry(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            raise SkyblockUpdatedError

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
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Carpentry EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.CarpentryColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

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

    @commands.command(name='runecrafting', description='Shows your Runecrafting statistics.')
    async def runecrafting(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            raise SkyblockUpdatedError

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Runecrafting stats.")

        xpForMax = target_profile['data']['levels']['runecrafting']['xp']
        of = self.RuneCraftingCap - xpForMax

        if of <= 0:
            of = 0

        xpForNext = target_profile['data']['levels']['runecrafting']['xpForNext']
        if xpForNext is None or xpForNext <= 0:
            xpForNext = 0

        xpNow = target_profile['data']['levels']['runecrafting']['xpCurrent']
        xpMax = xpForNext - xpNow
        if xpMax <= 0:
            xpMax = 0

        embed = discord.Embed(
            title='Runecrafting Level for ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Runecrafting EXP: ** ' + self.separator.format(round(int(xpForMax))),
            color=self.RunecraftingColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)

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

    """ DUNGEONS"""

    @commands.command(name='dungeons', aliases=['dungeon', 'catacombs', 'cata'],
                      description='Shows your Dungeoneering statistics.')
    async def dungeons(self, ctx, name, pname=None):
        nameApi = requests.get(f'{self.MojangUrl}{name}').json()
        target_profile = None

        async with ctx.session.get(self.SkyV2 + name) as api:
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

        healer = target_profile['data']['dungeons']['classes']['healer']['experience']['level']
        mage = target_profile['data']['dungeons']['classes']['mage']['experience']['level']
        tank = target_profile['data']['dungeons']['classes']['tank']['experience']['level']
        bers = target_profile['data']['dungeons']['classes']['berserk']['experience']['level']
        archer = target_profile['data']['dungeons']['classes']['archer']['experience']['level']
        fe = target_profile['data']['dungeons']['catacombs']['floors']['0']['stats']['tier_completions'] if '0' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0
        f1 = target_profile['data']['dungeons']['catacombs']['floors']['1']['stats']['tier_completions'] if '1' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0
        f2 = target_profile['data']['dungeons']['catacombs']['floors']['2']['stats']['tier_completions'] if '2' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0
        f3 = target_profile['data']['dungeons']['catacombs']['floors']['3']['stats']['tier_completions'] if '3' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0
        f4 = target_profile['data']['dungeons']['catacombs']['floors']['4']['stats']['tier_completions'] if '4' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0
        f5 = target_profile['data']['dungeons']['catacombs']['floors']['5']['stats']['tier_completions'] if '5' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0
        f6 = target_profile['data']['dungeons']['catacombs']['floors']['6']['stats']['tier_completions'] if '6' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0
        f7 = target_profile['data']['dungeons']['catacombs']['floors']['7']['stats']['tier_completions'] if '7' in \
                                                                                                            target_profile[
                                                                                                                'data'][
                                                                                                                'dungeons'][
                                                                                                                'catacombs'][
                                                                                                                'floors'] else 0

        print(
            f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] looked at {name}'s {pname} Dungeons stats.")

        embed = discord.Embed(
            title='Dungeon Stats For ' + nameApi['name'] + ' On Profile ' + pname,
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Dungeon EXP:** ' + (
                str(round(target_profile['data']['dungeons']['catacombs']['level']['xp'], 2))),

        )
        embed.set_thumbnail(url=self.McHeads + name)
        embed.set_footer(text=f'Requested by {ctx.message.author}.')
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Catacombs Level**',
                        value=str(target_profile['data']['dungeons']['catacombs']['level']['level']))
        embed.add_field(name='**EXP Until Next Level**', value=str(
            target_profile['data']['dungeons']['catacombs']['level']['xpForNext'] -
            target_profile['data']['dungeons']['catacombs']['level']['xpCurrent']))
        if target_profile['data']['dungeons']['catacombs']['visited']:
            embed.add_field(name='**Highest Floor\nIn Catacombs**',
                            value=str(target_profile['data']['dungeons']['catacombs']['highest_floor']).replace('_',
                                                                                                                ' ').replace(
                                'f', 'F'), inline=False)
        else:
            await ctx.send('You have never visited Dungeons!')

        if target_profile['data']['dungeons']['master_catacombs']['visited']:
            embed.add_field(name='**Highest Floor\nIn Master Mode**',
                            value=str(target_profile['data']['dungeons']['master_catacombs']['highest_floor']).replace(
                                '_', ' ').replace('floor', 'Master'), inline=True)

        embed.add_field(name='Class Levels',
                        value=f'```yaml\nHealer: {healer} \nMage: {mage} \nTank: {tank}\nBerserker: {bers} \nArcher: {archer}```',
                        inline=False)
        embed.add_field(name='Times Completed:',
                        value=f'```yaml\nEntrance: {fe} \nF1: {f1} \nF2: {f2} \nF3: {f3}\nF4: {f4} \nF5: {f5} \nF6: {f6} \nF7: {f7}```',
                        inline=False)

        await ctx.send(embed=embed)
    """ SLAYERS """

    @commands.command(name='slayer', aliases=['slayers'],
                      description='Shows all of your Zombie, Spider, Wolf and Enderman Slayer statistics.')
    async def slayers(self, ctx, name, pname=None):
        nameApi = requests.get(self.MojangUrl + name).json()
        target_profile = None

        async with ctx.session.get(self.SkyV2 + name) as api:
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
            url=f'{self.SkyShiiyuStats}{name}/{pname}',
            description='**Total Slayer EXP:** ' + self.separator.format(int(target_profile['data'][
                                                                                 'slayer_xp'])) + 'XP' + '\n ***Total Coins Spent on Slayers: ***' + self.separator.format(
                int(target_profile['data']['slayer_coins_spent']['total'])) + ' coins',
            color=self.SlayersColor
        )

        # Contents of discord embed
        embed.set_author(name=f'Requested by {ctx.message.author.display_name}.', icon_url=ctx.message.author.display_avatar.url)
        embed.set_thumbnail(url=self.McHeads + name)
        embed.timestamp = ctx.message.created_at

        embed.add_field(name='**Revenant Horror \nLevel**',
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
        embed.add_field(name='**Tarantula Broodfather \nGathered XP**',
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
        embed.add_field(name='**Coins Spent on \nSven Slayer**',
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

def setup(bot):
    bot.add_cog(Skyblock(bot))
