from utils.default import config

config = config()
owners = config["owners"]

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
