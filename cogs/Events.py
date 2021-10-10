# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from datetime import datetime
from logging import getLogger
from os import getpid

import apscheduler.schedulers.asyncio
import discord
from discord import HTTPException
from discord.ext import commands, tasks
from discord.ext.commands import (
    MissingPermissions,
    CheckFailure,
    MaxConcurrencyReached,
    CommandOnCooldown,
)
from psutil import Process

from cogs.Music import music_
# from lib.db import db
from utils import default
from utils.checks import GuildNotFound
from utils.vars import *

getLogger("events")
owners = default.config()["owners"]
bla = {}
default.MakeBlackList(bla)

scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()


async def Error(self, ctx, err):
    logs_channel = self.bot.get_channel(self.config["edoc_logs"])
    embed = discord.Embed(
        title="**Error!**", color=red, timestamp=ctx.message.created_at, description=err
    )
    await logs_channel.send(embed=embed)
    error(msg="Error Error")


async def Info(self, ctx, msg):
    non_critical_logs_channel = self.bot.get_channel(
        self.config["edoc_non_critical_logs"]
    )
    embed = discord.Embed(
        title="**Info!**",
        color=orange,
        timestamp=ctx.message.created_at,
        description=msg,
    )
    await non_critical_logs_channel.send(embed=embed)
    error(msg="Info message has been sent msg = " + msg)


class Events(commands.Cog, description="Event handling if u can see this ping the dev"):
    def __init__(self, bot):
        # self.blacklist = Blacklist
        self.bot = bot
        self.ready = False
        self.config = bot.config
        self.process = Process(getpid())
        self.scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()
        self.critlogschannel = self.config["edoc_logs"]
        self.noncritlogschannel = self.config["edoc_non_critical_logs"]
        self.db = self.bot.db
        # self.db.autosave(self.scheduler)

    async def erroremb(self, ctx, *, description: str, footer=None, title=None):
        """@summary creates a discord embed so i can send it with x details easier"""
        embed = discord.Embed(description=description, color=colors["error"])
        if title:
            embed.title = title
        if footer:
            embed.set_footer(text=footer)
        await ctx.send(embed=embed)

    async def permsemb(self, ctx, *, permissions: str):
        """@summary creates a discord embed so i can send it with x details easier"""
        embed = discord.Embed(
            title=":x: You are missing permissions",
            description=f"You need the following permission(s) to use {ctx.prefix}{ctx.command.qualified_name}:\n{permissions}",
            color=colors["error"],
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """guild thingos"""
        to_send = next(
            (
                chan
                for chan in sorted(guild.channels, key=lambda x: x.position)
                if chan.permissions_for(guild.me).send_messages
                and isinstance(chan, discord.TextChannel)
            ),
            None,
        )
        self.db.execute("INSERT OR IGNORE INTO guilds (id) VALUES (?)", (guild.id,))
        channel = self.bot.get_channel(guild.system_channel) or to_send
        await channel.send("Thank you for inviting me to the server")
        await channel.send("Please do ~help to get started")
        # await channel.send(
        #    "also if edoC fails it is because your servers guildID didn't get put into the database please contact the dev about it \n*(you can find him in ~info)")
        print(f"edoC has Joined {guild.name} it has {len(guild.members)} members ")

    # async def update_db(self):
    #    members = self.bot.get_all_members()
    #    for member in members:
    #        self.db.execute("INSERT OR IGNORE INTO User (UserID) VALUES (?)", member.id)
    #    for server in self.bot.guilds:
    #        print(server.name)
    #        admins = None  # {}
    #        # `for member in guild.members:
    #        #    if
    #        #            admins += members
    #        # inthings = [server.id, self.config["default_prefix"], server.name, admins] #
    #        self.db.execute("INSERT OR IGNORE INTO guilds (GuildID, Prefix, GuildName, GuildAdmins) VALUES (?, ?, ?, ?);",
    #                   (server.id, self.config["default_prefix"], server.name, admins))
    #
    #    print("updated db")
    #    await asyncio.sleep(21600.0)

    # async def update_db(self):
    #    members = self.bot.get_all_members()
    #    for member in members:
    #        self.db.execute("INSERT OR IGNORE INTO User (UserID) VALUES (?)", member.id)
    #    for server in self.bot.guilds:
    #        admins = None  # {}
    #        #`for member in guild.members:
    #        #    if
    #        #            admins += members
    #        # inthings = [server.id, self.config["default_prefix"], server.name, admins] #
    #        self.db.execute("INSERT OR IGNORE INTO guilds (GuildID, Prefix, GuildName, GuildAdmins) VALUES (?, ?, ?, ?);", (server.id, self.config["default_prefix"], server.name, admins))
    #    self.db.commit()
    #    print("updated db")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.CommandNotFound):
            try:
                if self.bot.settings[ctx.guild.id]["commanderrors"]:
                    await self.erroremb(
                        ctx,
                        description=f"The command you have requested is not found. \nPlease make sure you typed it out right",
                    )
            except KeyError:
                await self.bot.add_setting(ctx.guild.id)
        elif isinstance(err, commands.BadArgument):
            pass

        elif isinstance(err, commands.NotOwner):
            await self.erroremb(
                ctx,
                description=f"You must be the owner of {ctx.me.display_name} to use `{ctx.prefix}{ctx.command}`",
            )

        elif isinstance(err, commands.MissingRequiredArgument):
            # await self.erroremb(ctx,
            #                    description=f"Invalid Command Format: {ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}",
            #                    footer=f"Please use {ctx.prefix}help {ctx.command.qualified_name} for more info")
            missing = f"{str(err.param).split(':')[0]}"
            command = f"{ctx.prefix}{ctx.command}"  # {ctx.command.signature}"

            await self.erroremb(
                ctx,
                title=f"\N{WARNING SIGN} | MissingArguments",
                description=f"You forgot the `{missing}` parameter when using   `{command}`!",
                footer=f"Please use {ctx.prefix}help {ctx.command.qualified_name} for more info",
            )

        elif isinstance(err, commands.TooManyArguments):
            await self.erroremb(
                ctx,
                description=f"You called the {ctx.command.qualified_name} command with too many arguments.",
            )
        elif isinstance(err, commands.CommandInvokeError):
            error = default.traceback_maker(err.original)
            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{error}")
        elif isinstance(err, commands.CommandInvokeError):
            original = err.original
            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )
            if isinstance(original, discord.Forbidden):
                await ctx.send("I do not have permission to execute this action.")
            elif isinstance(original, discord.NotFound):
                await ctx.send(f"This entity does not exist: {original.text}")
            elif isinstance(original, discord.HTTPException):
                await ctx.send(
                    "Somehow, an unexpected error occurred. Try again later?"
                )

        elif isinstance(err, MissingPermissions):
            await self.permsemb(
                ctx, permissions=f"{', '.join(err.missing_permissions)}"
            )
        elif isinstance(err, CheckFailure):
            await self.erroremb(
                ctx,
                description=f"One or more permission checks have failed\nif you think this is a bug please contact us at\nhttps://dsc.gg/edoc",
            )
        elif isinstance(err, MaxConcurrencyReached):
            await self.erroremb(
                ctx=ctx,
                description="You've reached max capacity of command usage at once, please finish the previous one...",
            )

        elif isinstance(err, CommandOnCooldown):
            await self.erroremb(
                ctx=ctx,
                description=f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.",
            )
        elif isinstance(err, HTTPException):
            await self.erroremb(
                ctx=ctx, description=f"The returned message was too long"
            )
        elif isinstance(err, GuildNotFound):
            await self.erroremb(
                ctx=ctx, description=f"You can only use this command in a server"
            )
        else:
            print("Unknown error!")
            await self.erroremb(
                ctx,
                description="Sorry but this is an unknown error the devs has been notified!",
            )
            critlogschannel = self.bot.get_channel(self.critlogschannel)
            await critlogschannel.send(
                f"{ctx.message.author.mention} [in {ctx.message.guild.id}, #{ctx.message.channel}] made an error typing a command.```py\n{err}```"
            )

    @tasks.loop(hours=1, count=1, reconnect=True)
    async def Leave_Guild(self, guildid: int):
        guild = await self.bot.get_guild(guildid)
        if guild:
            print(guild)
            return
        else:
            self.db.execute("DELETE FROM guilds WHERE id=$1", guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # await self.remove_guild.start
        print(f"edoc has left {guild.name} it had {len(guild.members)} members")

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        if before.name != after.name:
            embed = discord.Embed(
                title="Username change",
                colour=after.colour,
                timestamp=datetime.utcnow(),
            )
            embed.set_footer(
                text=f"{before.name} {f'> {after.name}' if before.name != after.name else ''}"
            )

            fields = [("Before", before.name, False), ("After", after.name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = discord.Embed(
                title="Discriminator change",
                colour=after.colour,
                timestamp=datetime.utcnow(),
            )
            embed.set_footer(
                text=f"{before.name} {f'> {after.name}' if before.name != after.name else ''}"
            )

            fields = [
                ("Before", before.discriminator, False),
                ("After", after.discriminator, False),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

        # if before.display_avatar.url != after.display_avatar.url:
        #    embed = discord.Embed(title="Avatar change",
        #                          description="New image is below, old to the right.",
        #                          colour=blue)

    #
    #    embed.set_thumbnail(url=before.display_avatar.url)
    #    embed.set_image(url=after.display_avatar.url)
    #    embed.set_footer(
    #        text=f"{before.name} {f'> {after.name}' if before.name != after.name else ''}\n fullname: {before}")
    #    await noncritlogschannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        if before.display_name != after.display_name:
            embed = discord.Embed(
                title="Nickname change",
                colour=after.colour,
                timestamp=datetime.utcnow(),
            )

            fields = [
                ("Before", before.display_name, False),
                ("After", after.display_name, False),
            ]
            embed.set_footer(
                text=f"{before.name} {f'> {after.name}' if before.name != after.name else ''}"
            )

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

        elif before.roles != after.roles:
            embed = discord.Embed(
                title="Role updates", colour=after.colour, timestamp=datetime.utcnow()
            )
            embed.set_footer(
                text=f"{before.name} {f'> {after.name}' if before.name != after.name else ''}"
            )
            fields = [
                ("Before", ", ".join([r.name for r in before.roles]), False),
                ("After", ", ".join([r.name for r in after.roles]), False),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_footer(
                text=f"{before.name} {f'> {after.name}' if before.name != after.name else ''}"
            )

            await noncritlogschannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        if not after.author.bot:
            if before.content != after.content:
                embed = discord.Embed(
                    title="Message edit",
                    description=f"Edit by {after.author.display_name}.",
                    colour=after.author.colour,
                    timestamp=datetime.utcnow(),
                )

                fields = [
                    ("Before", before.content, False),
                    ("After", after.content, False),
                ]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                try:
                    await noncritlogschannel.send(embed=embed)
                except HTTPException:
                    pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
            if not message.author.bot:
                embed = discord.Embed(
                    title="Message deletion",
                    description=f"Action by {message.author.display_name}.\nIn {message.channel}\nIn {message.channel.guild}",
                    colour=message.author.colour,
                    timestamp=datetime.utcnow(),
                )

                fields = [("Content", message.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                try:
                    await noncritlogschannel.send(embed=embed)
                except HTTPException:
                    await noncritlogschannel.send(
                        embed=discord.Embed(
                            title="Message deletion",
                            description=f"Action by {message.author.display_name}.\nIn {message.channel}\nIn{message.channel.guild}",
                            colour=message.author.colour,
                            timestamp=datetime.utcnow(),
                        )
                    )
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel:
            if member.id == self.bot.user.id:
                return

            elif not before.channel.guild.me.voice:
                return

            elif after.channel is None:
                player = music_.get_player(guild_id=before.channel.guild.id)
                if player:
                    try:
                        await player.stop()
                        await player.delete()
                    except Exception:
                        pass
                if len(before.channel.members) == 1:
                    guild = self.bot.get_guild(before.channel.guild.id)
                    await guild.voice_client.disconnect()

    @commands.Cog.listener()
    async def premium_guild_subscription(self, ctx):
        await ctx.send(f"{ctx.auther} just boosted the server :party:")


def setup(bot):
    bot.add_cog(Events(bot))
