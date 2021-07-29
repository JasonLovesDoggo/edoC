import discord
from utils import default
from discord.ext import commands
from discord.ext.commands import (
    bot_has_permissions,
    has_permissions,
    is_owner,
)
from utils import default

owners = default.config()["owners"]

def is_owner(ctx):
    """ Checks if the author is one of the owners """
    return ctx.author.id in owners
"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
def is_mod():
    """Is the user a moderator ?"""

    async def pred(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        permissions: discord.Permissions = ctx.channel.permissions_for(
            ctx.author
        )
        return permissions.manage_messages

    return commands.check(pred)


def is_admin():
    """Is the user Admin ? as @check"""

    async def pred(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        permissions: discord.Permissions = ctx.channel.permissions_for(
            ctx.author
        )
        return permissions.administrator

    return commands.check(pred)


async def is_user_admin(ctx):
    """Is the user Admin ? as function"""

    if await ctx.bot.is_owner(ctx.author):
        return True

    permissions: discord.Permissions = ctx.channel.permissions_for(ctx.author)

    return permissions.administrator


"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

async def check_permissions(ctx, perms, *, check=all):
    """ Checks if author has permissions to a permission """
    if ctx.author.id in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def Has_permissions(*, check=all, **perms):
    """ discord.Commands method to check if author has permissions """
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
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


def can_handle(ctx, permission: str):
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(ctx.channel, discord.DMChannel) or getattr(ctx.channel.permissions_for(ctx.guild.me), permission)
