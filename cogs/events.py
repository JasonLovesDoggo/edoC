import asyncio

import discord
from discord.utils import find
from discord.ext import commands
from discord.ext.commands import errors
from cogs.mod import BannedUsers, BannedU
from utils import default
from lib.db import db
import os
import psutil
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.vars import *
logging.getLogger("events")
owners = default.config()["owners"]


async def Error(self, ctx, err):
    logs_channel = self.bot.get_channel(self.config["edoc_logs"])
    embed = discord.Embed(title="**Error!**",
                          color=red,
                          timestamp=ctx.message.created_at,
                          description=err)
    await logs_channel.send(embed=embed)
    logging.error(msg="Error Error")

async def Info(self, ctx, msg):
    non_critical_logs_channel = self.bot.get_channel(self.config["edoc_non_critical_logs"])
    embed = discord.Embed(title="**Info!**",
                          color=orange,
                          timestamp=ctx.message.created_at,
                          description=msg)
    await non_critical_logs_channel.send(embed=embed)
    logging.error(msg="Info message has been sent msg = " + msg)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ready = False
        self.config = default.config()
        self.process = psutil.Process(os.getpid())
        self.scheduler = AsyncIOScheduler()
        self.owner_commands = 0
        self.normal_commands = 0
        self.logs_channel = self.bot.get_channel(self.config["edoc_logs"])
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.update_db())
        loop.run_until_complete(task)

    async def erroremb(self, ctx, *, description: str):
        """@summary creates a discord embed so i can send it with x details easier"""
        embed = discord.Embed(
            title='Error!',
            description=description,
            color=colors["red"]
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild, member):
        """guild thingos """
        general = find(lambda x: x.name == 'general' or 'General', guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            wlcmchannel = general
        else:
            wlcmchannel = None
        channel = self.bot.get_channel(wlcmchannel.id)
        await channel.send("Thank you for inviting me to the server")
        await channel.send("Please do ~help to get started")
        annoy = member

    async def update_db(self):
        members = self.bot.get_all_members()
        for member in members:
            db.execute("INSERT OR IGNORE INTO User (UserID) VALUES (?)", member.id)
        for server in self.bot.guilds:
            print(server.name)
            admins = None  # {}
            # `for member in guild.members:
            #    if
            #            admins += members
            # inthings = [server.id, self.config["default_prefix"], server.name, admins] #
            db.execute("INSERT OR IGNORE INTO guilds (GuildID, Prefix, GuildName, GuildAdmins) VALUES (?, ?, ?, ?);",
                       (server.id, self.config["default_prefix"], server.name, admins))
        db.commit()
        print("updated db")

    #async def update_db(self):
    #    members = self.bot.get_all_members()
    #    for member in members:
    #        db.execute("INSERT OR IGNORE INTO User (UserID) VALUES (?)", member.id)
    #    for server in self.bot.guilds:
    #        admins = None  # {}
    #        #`for member in guild.members:
    #        #    if
    #        #            admins += members
    #        # inthings = [server.id, self.config["default_prefix"], server.name, admins] #
    #        db.execute("INSERT OR IGNORE INTO guilds (GuildID, Prefix, GuildName, GuildAdmins) VALUES (?, ?, ?, ?);", (server.id, self.config["default_prefix"], server.name, admins))
    #    db.commit()
    #    print("updated db")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.CommandNotFound):
            await self.erroremb(ctx, description=f'The command you have requested is not found. \nPlease make sure you typed it out right',)

        elif isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await self.erroremb(ctx, description=helper)

        elif isinstance(err, errors.MissingRequiredArgument):
            await self.erroremb(ctx, description="Please make sure to fill out all the arguments")
        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)
            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{error}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await self.erroremb(ctx=ctx, description="You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await self.erroremb(ctx=ctx, description="This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        else:
            print('Unknown error!')
            await self.erroremb(ctx, description="Sorry but this is an unknown error the devs has been notified!")
            await self.logs_channel.send(f"{ctx.message.author} [in {ctx.message.guild}, #{ctx.message.channel}] made an error typing a command. The error is unknown!")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"edoc has left {guild.name} it had {len(guild.members)} members")
        # todo add a thing to remove said guild from the database after an hour

    @commands.Cog.listener()
    async def on_member_join(self, guild, member):
        channel = guild.sys
        # if not self.config[f"join_message"]:
        #    return
        #
        # try:
        #    to_send = sorted([chan for chan in guild.channels if
        #                      chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)],
        #                     key=lambda x: x.position)[0]
        # except IndexError:
        #    pass
        # else:
        #    join_msg = self.config[f"join_message"]
        #    await to_send.send(f"{join_msg} {user.mention}")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.check(BannedU)
        self.normal_commands + 1
        if ctx.message.author.id in self.config[f"owners"]:
            self.owner_commands + 1
        if ctx.author.id in BannedUsers:
            blocked = True
        else:
            blocked = False
        try:
            print(
                f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content} > Blocked {blocked}")
            logging.basicConfig(filename="log.log",
                                format='%(asctime)s %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S %p',
                                level=logging.INFO,
                                filemode='w+')
            logging.info(f'{ctx.guild.name} > ')  # {ctx.author} > {ctx.message.clean_content}
        except AttributeError:
            print(f"Private message > {ctx.author} > {ctx.message.clean_content} > Blocked {blocked}")
            logging.info(f'Private message > ')
            # {ctx.author} > {ctx.message.clean_content}

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        logschannel = self.bot.get_channel(self.config["edoc_logs"])
        if not self.ready:
            self.ready = True
            self.scheduler.start()
            await logschannel.send(f"{self.bot.user} has been booted up")

            if not hasattr(self.bot, "uptime"):
                self.bot.uptime = datetime.utcnow()

            # Check if user desires to have something other than online
            status = self.config["status_type"].lower()
            status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

            # Check if user desires to have a different type of activity
            activity = self.config["activity_type"].lower()
            activity_type = {"listening": 2, "watching": 3, "competing": 5}

            await self.bot.change_presence(
                activity=discord.Game(
                    type=activity_type.get(activity, 0), name=self.config["activity"]
                ),
                status=status_type.get(status, discord.Status.online)
            )
            totalmembers = sum(g.member_count for g in self.bot.guilds)
            # Indicate that the bot has successfully booted up
            print(
                f"Ready: {self.bot.user} | Total members {totalmembers} | Guild count: {len(self.bot.guilds)} | Guilds")
            guilds = {}
            for Server in self.bot.guilds:
                try:
                    to_send = sorted([chan for chan in Server.channels if
                                      chan.permissions_for(Server.me).send_messages and isinstance(chan,
                                                                                                   discord.TextChannel)],
                                     key=lambda z: z.position)[0]
                except IndexError:
                    pass
                else:
                    invite_link = await to_send.create_invite(max_uses=1, unique=False, temporary=True)
                if Server.id in guilds:
                    verified: bool = True
                else:
                    verified: bool = False
                gprefix = db.field('SELECT Prefix FROM guilds WHERE GuildID = ?', Server.id)
                print(
                    f"{Server.id} ~ {Server} ~ {Server.owner} ~ {Server.member_count} ~ {invite_link} ~ Prefix {gprefix}")
        else:
            print(f"{self.bot.user} Reconnected")
            logging.log("Bot reconnected")
            await logschannel.send(f"{self.bot.user} has been reconnected")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, prev, cur):
        user = f"{member.name}#{member.discriminator}"
        if cur.afk and not prev.afk:
            print(f"{user} went AFK!")
        elif prev.afk and not cur.afk:
            print(f"{user} is no longer AFK!")
        elif cur.self_mute and not prev.self_mute:  # Would work in a push to talk channel
            print(f"{user} stopped talking!")
        elif prev.self_mute and not cur.self_mute:  # As would this one
            print(f"{user} started talking!")

    @commands.Cog.listener()
    async def premium_guild_subscription(self, ctx):
        await ctx.send(f"{ctx.auther} just boosted the server :party:")

def setup(bot):
    bot.add_cog(Events(bot))
