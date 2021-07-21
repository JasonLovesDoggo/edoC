import os
import platform
import sys
import time
import psutil
import discord
from datetime import datetime
from discord.ext import commands
from utils.vars import *
from utils import default
from utils.data import get_prefix
from lib.db import db


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.PADDING = 9
        self.process = psutil.Process(os.getpid())
        self.event = self.bot.get_cog("Events")
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.utcnow()

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
        perms.administrator = True
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

    @commands.command(aliases=["code"])
    async def source(self, ctx):
        """ Check out my source code <3 """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT.
        await ctx.send(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/JakeWasChosen/edoC")

    @commands.command()
    async def todo(self, ctx):
        """reads the todo.txt file"""
        file = open("todo.txt", "r")
        the_thing = file.read()
        await ctx.send(the_thing)
        file.close()

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
            name=f"Developer (bio)[https://bio.link/edoc]",
            value=", ".join([str(self.bot.get_user(x)) for x in self.config["owners"]]),
            inline=True
        )
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Total Members", value=totalmembers)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )",
                        inline=True)
        embed.add_field(name="Commands Loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="Commands Ran By Owners", value=None)
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
        info["Python Version"] = f"{platform.python_version()}"
        info["Avg users/server"] = f"{avgmembers:,.2f}"
        info["commands ran since restart"] = self.event.normal_commands
        info["Commands ran by owners"] = self.event.owner_commands
        info["Bot owners"] = len(self.config["owners"])
        info["Bot mods"] = len(self.config["mods"])
        info["Prefix in this server"] = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?",
                                                 ctx.guild.id)  # get_prefix(self.bot, ctx)
        info["Total members"] = totalmembers
        info["blank"] = None
        info["Ram usage"] = f"{ramUsage:.2f} MB"
        info["Developer"] = "Jake CEO of annoyance#1904"

        for k, v in info.items():
            pad = ' ' * (self.PADDING - len(str(v)))
            em.description += f"`{pad}{v}`: **{k}**\n"
        em.set_footer(text="bot owners are excluded from command stats")
        await ctx.send(content=f"About **{ctx.bot.user}** | **{self.config['version']}**", embed=em)
        await ctx.send("||https://bio.link/edoC||")

    @commands.command()
    async def developer(self, ctx):
        emb = discord.Embed(title="Jason",
                            color=blue,
                            timestamp=ctx.message.created_at
                            )
        devinfo = {}
        devinfo["yes"] = "no"
        for k, v in devinfo.items():
            pad = ' ' * (self.PADDING - len(str(v)))
            emb.description += f"`{pad}{v}`: **{k}**\n"

        emb.set_footer(text="Please consider donating")

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
