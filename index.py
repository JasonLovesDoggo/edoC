import os
import discord
from discord.ext.commands.context import Context
from utils.default import edoC, config
config = config()
#TODO add a fully not erroring get_prefix
bot = edoC()


NO_LOAD_COG = ''

async def process_commands(self, message):
    ctx = await self.get_context(message, cls=Context)

    if ctx.command is not None and ctx.guild is not None:
        if message.author.id in self.banlist:
            await ctx.send("You are banned from using commands.")

        elif not self.ready:
            await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

        else:
            await self.invoke(ctx)


try:
    bot.load_extension("jishaku")
    for file in os.listdir("cogs"):
        if NO_LOAD_COG:
            if file.startswith(NO_LOAD_COG):
                continue
        if file.endswith(".py"):
            name = file[:-3]
            bot.load_extension(f"cogs.{name}")
except Exception:
    raise ChildProcessError("Problem with one of the cogs/utils")


try:
    bot.run(config["token"], reconnect=True)
except Exception as e:
    print(f"Error when logging in: {e}")
