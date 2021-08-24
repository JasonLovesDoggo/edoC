import discord

from discord.ext import commands

from utils.vars import *

# from lib.db import db

"""
def get_prefix(bot, message):
    try:
        if not message.guild:
            return config["default_prefix"]
        else:
            prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
            if prefix:
                return commands.when_mentioned_or(prefix)(bot, message)
            else:
                return config["default_prefix"]
    except AttributeError:
        return config["default_prefix"]



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
        try:
            for page in self.paginator.pages:
                emby = discord.Embed(description=page, color=random_color())
                await destination.send(embed=emby)
        except discord.Forbidden:
            await destination.send("Couldn't send help to you due to blocked DMs...")

    async def send_error_message(self, err):
        embed = discord.Embed(title="Error", description=err, color=error)
        channel = self.get_destination()
        await channel.send(embed=embed)
