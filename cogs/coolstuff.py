# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os

import psutil
from discord.ext import commands


# import dsc


class CoolStuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.process = psutil.Process(os.getpid())
        # noinspection PyUnresolvedReferences
        # self.client = dsc.Client(default.config["dsc_gg_api_key"])
        # self.app = self.client.get_app(5297746284630572)

    # @commands.check(is_owner or is_mod)
    # @commands.group(aliases=["ds"])
    # async def dscgg(self, ctx):
    #    """ Stuff with the dsc.gg api
    #        With the ~ds link command please use hex for the color"""
    #    if ctx.invoked_subcommand is None:
    #        await ctx.send_help(str(ctx.command))


#
# @dscgg.command()
# async def link(self, ctx, hexcolor, name, redirect: str, imageurl: str = None):
#    """ Usage ~ds link 0xFFFFFF edoc bot.com (#optional#) imguer.com/img """
#    embed = dsc.Embed(
#        color=hexcolor,
#        title=name,
#        image=imageurl
#    )
#    res = await self.client.create_link(name, redirect, embed=embed)
#
#    if res.status == 200:
#        await ctx.send('Link created!')
#    elif res.status == 429:
#        await ctx.send("Rate limted please wait a little bit")
#    else:
#        await ctx.send('An error occurred.')


def setup(bot):
    bot.add_cog(CoolStuff(bot))
