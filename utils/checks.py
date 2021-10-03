
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from discord.ext import commands
from discord.ext.commands import CommandError

from utils.default import config

config = config()
owners = config["owners"]



class GuildNotFound(CommandError):
    pass

async def dick_check(ctx, id):
    banned_u = ctx.bot.banned_users
    if id in banned_u:
        return await ctx.error('You\'re currently banned from using edoC\nPlease join the support server to appeal')

async def stealer_check(ctx, id, bot):
    msg = await ctx.invis('Checking if you steal code...')
    stealers = bot.get_data('codestealers')
    if id in stealers:
        return await ctx.error('Hey bro you steal code not cool')
    await msg.delete()
    return False


def guild_only():
    """Custom commands.guild_only with different error checking."""

    def pred(ctx):
        if ctx.guild is None:
            raise GuildNotFound
        return True

    return commands.check(pred)


async def check_priv(ctx, member):
    """ Custom (weird) way to check permissions when handling moderation commands """
    try:
        # Self checks
        if member == ctx.author:
            return await ctx.send(f"You can't {ctx.command.name} yourself")
        if member.id == ctx.bot.user.id:
            return await ctx.send("So that's what you think of me huh..? sad ;-;")

        # Check if user bypasses
        if ctx.author.id == ctx.guild.owner.id:
            return False

        # Now permission check
        if member.id in owners:
            if ctx.author.id not in owners:
                return await ctx.send(f"I can't {ctx.command.name} my creator ;-;")
            else:
                pass
        if member.id == ctx.guild.owner.id:
            return await ctx.send(f"You can't {ctx.command.name} the owner, lol")
        if ctx.author.top_role == member.top_role:
            return await ctx.send(f"You can't {ctx.command.name} someone who has the same permissions as you...")
        if ctx.author.top_role < member.top_role:
            return await ctx.send(f"Nope, you can't {ctx.command.name} someone higher than yourself.")
    except Exception:
        pass
