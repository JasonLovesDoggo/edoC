# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from typing import Optional

from discord import utils
from discord.ext.commands import Cooldown


# Useage
# @dynamic_cooldown(api_cooldown, BucketType.user)


def api_cooldown(message) -> Optional[Cooldown]:
    print("cooldown")
    if message.author.guild_permissions.manage_messages:
        return Cooldown(1, 2)  # Low cooldown
    if message.author.id == message.bot.owner_id:
        return None  # No cooldown for me
    elif utils.get(message.author.roles, name="Nitro Booster"):
        return Cooldown(2, 5)  # 2 per 5s
    print("1")
    return Cooldown(1, 5)  # 1 per 5s


def pfp_cooldown(message) -> Optional[Cooldown]:
    if message.author.guild_permissions.manage_messages:
        return Cooldown(1, 2)  # Low cooldown
    if message.author.id == message.bot.owner_id:
        return None  # No cooldown for me
    elif utils.get(message.author.roles, name="Nitro Booster"):
        return Cooldown(2, 3)  # 2 per 5s
    return Cooldown(1, 3)  # 1 per 5s
