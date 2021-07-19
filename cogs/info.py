import time
import discord
import psutil
import os

from datetime import datetime
from discord.ext import commands
from edoC.utils.vars import *
from edoC.utils import default
from edoC.utils.data import get_prefix

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())
        self.config = default.config()

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command(aliases=["joinme", "join", "botinvite"])
    async def invite(self, ctx):
        """Sends you the bot invite link."""
        perms = discord.Permissions.none()
        perms.read_messages = True
        perms.send_messages = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.attach_files = True
        perms.add_reactions = True
        await ctx.send(
            f"**{ctx.author.name}**, use this URL to invite me\n<{discord.utils.oauth_url(self.bot.user.id, perms)}>")

    @commands.command()
    async def changehelp(self, ctx):
        """ Give Info on ~change """
        await ctx.send("""~change 
                        Commands:
                        avatar   Change avatar. 
                        nickname Change nickname. 
                        playing  Change playing status. 
                        username Change username. 

                        Type ~help command for more info on a command.
                        You can also type ~help category for more info on a category.""")

    @commands.command()
    async def source(self, ctx):
        """ Check out my source code <3 """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT.
        await ctx.send(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/JakeWasChosen/Cardinal")

    @commands.command()
    async def todo(self, ctx):
        """reads the todo.txt file"""
        file = open("todo.txt", "r")
        the_thing = file.read()
        await ctx.send(the_thing)
        file.close

    @commands.command(aliases=["supportserver", "feedbackserver"])
    async def botserver(self, ctx):
        """ Get an invite to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 819282410213605406:
            return await ctx.send(f"**Here you go {ctx.author.name} 🍻\n<{self.config['botserver']}>**")
        await ctx.send(f"**{ctx.author.name}** this is my home you know :3")

    @commands.command(aliases=["info", "stats", "status", "botinfo"])
    async def about(self, ctx):
        """ About the bot """

        ramUsage = self.process.memory_full_info().rss / 1024 ** 2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)
        totalmembers = sum(g.member_count for g in self.bot.guilds)
        embed = discord.Embed(colour=green)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Last boot", value=default.timeago(datetime.now() - self.bot.uptime), inline=True)
        embed.add_field(
            name=f"Developer{'' if len(self.config['owners']) == 1 else 's'}",
            value=", ".join([str(self.bot.get_user(x)) for x in self.config["owners"]]),
            inline=True
        )
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Total Members", value=totalmembers)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )",
                        inline=True)
        embed.add_field(name="Commands Loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="Commands Ran By Owners", value=self.bot.owner_commands)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)
        embed.set_footer(text=embedfooter)
        await ctx.send(content=f"ℹ About **{ctx.bot.user}** | **{self.config['version']}**", embed=embed)

    @commands.command(aliases=["bs"])
    async def botstats(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024 ** 2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)
        totalmembers = sum(g.member_count for g in self.bot.guilds)
        em = discord.Embed(title="WIP stats design",
                           colour=dark_blue,
                           timestamp=ctx.message.created_at,
                           description="")
        info = {}
        info["Discord.py version"] = discord.__version__
        info["Cool variable y"] = 7
        info["commands since restart"] = self.bot.normal_commands
        info["Cmds ran by owners"] = self.bot.owner_commands
        info["Bot owners"] = len(self.config["owners"])
        info["Prefix in this server"] = get_prefix(bot=self.bot, message=ctx.message)
        PADDING = 9
        for k, v in info.items():
            pad = ' ' * (PADDING - len(str(v)))
            em.description += f"`{pad}{v}`: **{k}**\n"
        em.set_footer(text="bot owners are excluded from command stats")
        await ctx.send(content=f"About **{ctx.bot.user}** | **{self.config['version']}**", embed=em)

    @commands.guild_only()
    @commands.command()
    async def emote(self, ctx, msg: str = None):
        """List all emotes in this server."""
        if msg:
            server, found = ctx.find_server(msg)
            if not found:
                return await ctx.send(server)
        else:
            server = ctx.message.server
        emojis = [str(x) for x in server.emojis]
        await ctx.say(" ".join(emojis))


def setup(bot):
    bot.add_cog(Information(bot))
