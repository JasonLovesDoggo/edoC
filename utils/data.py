import discord

from utils import permissions, default
from discord.ext.commands import AutoShardedBot, when_mentioned_or
from discord.ext import commands
from lib.db import db

config = default.config()

class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not permissions.can_handle(msg, "send_messages"):
            return

        await self.process_commands(msg)


def get_prefix(bot, message):
    try:
        if not message.guild:
            return config["default_prefix"]
        else:
            prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
            if prefix:
                return when_mentioned_or(prefix)(bot, message)
            else:
                return config["default_prefix"]
    except AttributeError:
        return config["default_prefix"]


"""
class HelpFormat(DefaultHelpCommand):
    def get_destination(self, no_pm: bool = False):
        if no_pm:
            return self.context.channel
        else:
            return self.context.author

    async def send_error_message(self, error):
        destination = self.get_destination(no_pm=True)
        await destination.send(error)

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages(no_pm=True)

    async def send_pages(self, no_pm: bool = False):
        try:
            if permissions.can_handle(self.context, "add_reactions"):
                await self.context.message.add_reaction(chr(0x2709))
        except discord.Forbidden:
            pass

        try:
            destination = self.get_destination(no_pm=no_pm)
            for page in self.paginator.pages:
                await destination.send(page)
        except discord.Forbidden:
            destination = self.get_destination(no_pm=True)
            await destination.send("Couldn't send help to you due to blocked DMs...")
            """


class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)
