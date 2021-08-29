# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021-2021. Jason Cameron                                                          +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from os import environ, listdir

from utils.default import edoC, config

config = config()
# TODO add a fully not erroring get_prefix
bot = edoC()
environ["JISHAKU_HIDE"] = "True"
environ["JISHAKU_NO_UNDERSCORE"] = "True"
NO_LOAD_COG = ''
#async def process_commands(self, message):
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
    bot.run(config["token"], reconnect=True)
except Exception as e:
    print(f"Error when logging in: {e}")
