# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from io import BytesIO

import discord
from PIL import Image

from utils.Context import edoCContext


# display_avatar
# todo make a system to get margority color from a user via display avatar user.color and more e.g. banner


async def get_majority_color(b: BytesIO) -> discord.Color:
    with Image.open(b) as target:
        smol = target.quantize(4)
        return discord.Color.from_rgb(*smol.getpalette()[:3])


async def get_user_color(ctx: edoCContext, user: discord.Member):
    Avatar = BytesIO(await ctx.author.avatar.read())
    Banner = BytesIO(await ctx.author.banner.read())
    AvatarColor = await get_majority_color(Avatar)
    BannerColor = await get_majority_color(Banner)
    RoleColor = user.colour
    return {"Banner": BannerColor, "Avatar": AvatarColor, "Role": RoleColor}
