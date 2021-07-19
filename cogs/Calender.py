import time
import discord
import psutil
import os

from datetime import datetime
from discord.ext import commands
from utils import default


class Calender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())


def setup(bot):
    bot.add_cog(Calender(bot))

# api key goes here 1d2433205d1e66f555aae1335493344aab350af82f177191dbe21998d80e9888 teamup api key
