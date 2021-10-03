# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021-2021. Jason Cameron                                                          +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import contextlib
import logging
from asyncio import get_event_loop
from logging.handlers import RotatingFileHandler
from os import environ, listdir

from utils.default import edoC, config

config = config()
# TODO add a fully not erroring get_prefix
environ["JISHAKU_HIDE"] = "True"
environ["JISHAKU_NO_UNDERSCORE"] = "True"
NO_LOAD_COG = 'API'


#@bot.after_invoke
#async def add_count(ctx):
#    db = bot.db
#    cc = await db.fetchrow('SELECT count FROM stats')  # current count
#    await db.execute('UPDATE stats SET count = ? WHERE count = ?', (cc + 1, cc))


# @bot.slash_command(guild_ids=[
#    819282410213605406])  # if guild_ids is not given, the command will be released globally, although it will take atmost 1 hour to release due to API limitations of Discord
# async def hello(
#        ctx,
#        name: Option(str, "Enter your name"),
#        gender: Option(str, "Choose your gender", choices=["Male", "Female", "Other"]),
#        age: Option(int, "Enter your age", required=False, default=18),
# ):
#    await ctx.send(f"Hello {name} {gender} {age}")

# async def process_commands(self, message):
#    ctx = await self.get_context(message, cls=Context)
#
#    if ctx.command is not None and ctx.guild is not None:
#        if message.author.id in self.banlist:
#            await ctx.send("You are banned from using commands.")
#
#        elif not self.ready:
#            await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")
#
#        else:
#            await self.invoke(ctx)
#
@contextlib.contextmanager
def setup_logging():
    try:
        FORMAT = "[%(asctime)s] [%(levelname)s]: %(message)s"
        DATE_FORMAT = "%d/%m/%Y (%H:%M:%S)"

        logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(
            filename="discord.log",
            mode="a",
            encoding="utf-8",
            maxBytes=33554432,
            backupCount=5,
        )  # maxBytes = 33554432 -> 32 mb
        file_handler.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT))
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT))
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)

        yield
    finally:
        handlers = logger.handlers[:]  # type: ignore
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)  # type: ignore

async def run():
    bot = edoC()
    try:
        bot.load_extension("jishaku")
        for file in listdir("cogs"):
            if NO_LOAD_COG:
                if file.startswith(NO_LOAD_COG):
                    continue
            if file.endswith(".py"):
                name = file[:-3]
                bot.load_extension(f"cogs.{name}")
    except Exception:
        raise ChildProcessError("Problem with one of the cogs/utils")

    try:
        with setup_logging():
            bot.run(config["token"], reconnect=True)
    except Exception as e:
        print(f"Error when logging in: {e}")

loop = get_event_loop()
loop.run_until_complete(run())
