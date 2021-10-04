# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from io import BytesIO
from typing import Any

import discord

from utils.Context import edoCContext
from utils.default import asyncify

display_avatar


@asyncify()
def get_majority_color(b: BytesIO) -> Any[Any, Any, discord.Color]:
    with Image.open(b) as target:
        smol = target.quantize(4)
        return discord.Color.from_rgb(*smol.getpalette()[:3])


async def get_user_color(ctx: edoCContext, user: discord.Member):
    pfp = user.avatar.read()
    pfpc = await get_majority_color(pfp)
    banner = user.banner.read()
    bannerc = get_majority_color(banner)
    rolec = user.colour
