# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021-2021. Jason Cameron                                                          +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import asyncio
import contextlib
import logging
from logging.handlers import RotatingFileHandler
from os import environ, listdir

from utils.db import Table
from utils.default import edoC, config

config = config()
# TODO add a fully not erroring get_prefix
environ["JISHAKU_HIDE"] = "True"
environ["JISHAKU_NO_UNDERSCORE"] = "True"
NO_LOAD_COGS = ["Config"]
bot = edoC()
try:
    bot.load_extension("jishaku")
    for file in listdir("cogs"):
        name = file[:-3]
        if len(NO_LOAD_COGS) > 1:
            if name in NO_LOAD_COGS:
                continue
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{name}")
except Exception:
    raise ChildProcessError("Problem with one of the cogs/utils")


# @bot.after_invoke
# async def add_count(ctx):
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
class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name="discord.state")

    def filter(self, record):
        if record.levelname == "WARNING" and "referencing an unknown" in record.msg:
            return False
        return True

@contextlib.contextmanager
def setup_logging():
    try:
        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("discord.state").addFilter(RemoveNoise())

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename="edoC.log",
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=5,
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
        )
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

def run_bot():
    loop = asyncio.get_event_loop()
    log = logging.getLogger()
    kwargs = {
        'command_timeout': 60,
        'max_size': 20,
        'min_size': 20,
    }
    try:
        pool = loop.run_until_complete(Table.create_pool(config['database']['uri'], **kwargs))
    except Exception as e:
        print('Could not set up PostgreSQL. Exiting.', e)
        log.exception('Could not set up PostgreSQL. Exiting.', e)
        return

    bot.pool = pool
    bot.run(config["token"], reconnect=True)


if __name__ == "__main__":
    try:
        with setup_logging():
            run_bot()
    except Exception as e:
        print(f"Error when logging in: \n{e}")
