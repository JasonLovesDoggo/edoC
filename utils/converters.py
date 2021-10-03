# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from urllib.parse import quote

from discord import NotFound, HTTPException, Member
from discord.ext.commands import Converter, BadArgument


async def authorOrReferenced(ctx):
    if ref := ctx.replied_reference:
        # Get referenced message author
        # if user reply to a message while doing this command
        return (
            ref.cached_message.author
            if ref.cached_message
            else (await ctx.fetch_message(ref.message_id)).author
        )
    return ctx.author

class MemberConverter(Converter, Member):
    async def convert(self, ctx, argument):
        ctx = await ctx.bot.get_context(message=ctx.message)
        try:
            return await authorOrReferenced(ctx) or await Member(argument)
        except Exception as e:
            print(e)
            return ctx.author

class UrlSafe(Converter):
    async def convert(self, ctx, argument: str):
        try:
            urlsafe = quote(argument)
        except ValueError:
            raise BadArgument("One ore more chars are invalid")
        return urlsafe

class BotUser(Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise BadArgument('Not a valid bot user ID.')
        try:
            user = await ctx.bot.fetch_user(int(argument))
        except NotFound:
            raise BadArgument('Bot user not found (404).')
        except HTTPException as e:
            raise BadArgument(f'Error fetching bot user: {e}')
        else:
            if not user.bot:
                raise BadArgument('This is not a bot.')
            return user
