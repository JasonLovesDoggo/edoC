import os
import discord
from discord.ext.commands.context import Context
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import default
from utils.data import Bot, MyNewHelp, get_prefix
import logging
from lib.db import db

config = default.config()

bot = Bot(
    command_prefix=get_prefix, prefix=get_prefix,
    owner_ids=config["owners"], case_insensitive=True, command_attrs=dict(hidden=True), help_command=MyNewHelp(),
    description='Relatively simply awesome bot. Developed by Jake CEO of annoyance#1904',
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents(
        # kwargs found at https://discordpy.readthedocs.io/en/latest/api.html?highlight=intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True, presences=True
    )
)


async def process_commands(self, message):
    ctx = await self.get_context(message, cls=Context)

    if ctx.command is not None and ctx.guild is not None:
        if message.author.id in self.banlist:
            await ctx.send("You are banned from using commands.")

        elif not self.ready:
            await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

        else:
            await self.invoke(ctx)


scheduler = AsyncIOScheduler()
db.autosave(scheduler)
try:
    bot.load_extension("jishaku")
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            name = file[:-3]
            bot.load_extension(f"cogs.{name}")
except Exception:
    raise ChildProcessError("Problem with one of the cogs/utils")

logging.basicConfig(
    filename=f"log.log",
    filemode="w",
    datefmt="%d-%b-%y %H:%M:%S",
    format="[{asctime}] {levelname:<10} | {name:<10}: {message}",
    style="{",
    level=logging.WARNING,
)

try:
    bot.run(config["token"], reconnect=True)
except Exception as e:
    print(f"Error when logging in: {e}")
