from typing import Optional
import discord
from discord.utils import get
from discord.ext.menus import MenuPages
from discord.ext.commands import Cog
from discord.ext.commands import command
from cogs.info import Menu

def syntax(command):
    cmd_and_aliases = " | ".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"`{cmd_and_aliases} {params}`"


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cmd_help(self, ctx, command):
        embed = discord.Embed(title=f"Help with `{command}`",
                              description=syntax(command),
                              colour=ctx.author.colour)
        embed.add_field(name="Command description", value=command.help)
        await ctx.send(embed=embed)

    @command(name="listhelp", aliases=["ls"], hidden=True)
    async def show_help(self, ctx, cmd: Optional[str]):
        """Shows this message."""
        if cmd is None:
            menu = MenuPages(source=Menu(ctx, list(self.bot.commands)),
                             delete_message_after=True,
                             timeout=60.0)
            await menu.start(ctx)

        else:
            if command := get(self.bot.commands, name=cmd):
                await self.cmd_help(ctx, command)

            else:
                await ctx.send("That command does not exist.")


def setup(bot):
    bot.add_cog(Help(bot))
