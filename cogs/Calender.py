
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from discord.ext import commands


class Calender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config


def setup(bot):
    bot.add_cog(Calender(bot))

# api key goes here 1d2433205d1e66f555aae1335493344aab350af82f177191dbe21998d80e9888 teamup api key
