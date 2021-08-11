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
import apscheduler.schedulers.asyncio
from utils.vars import *

logging.getLogger("events")
owners = default.config()["owners"]

scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()
db.autosave(scheduler)
async def  Error(self, ctx, err):
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
        self.scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()
        self.owner_commands = 0
        self.normal_commands = 0
        self.critlogschannel = self.bot.get_channel(self.config["edoc_logs"])
        self.allmembers = self.bot.get_all_members()
        self.guilds = self.bot.guilds
        self.noncritlogschannel = self.config["edoc_non_critical_logs"]
        self.update_db()

    async def erroremb(self, ctx, *, description: str):
        """@summary creates a discord embed so i can send it with x details easier"""
        embed = discord.Embed(
            description=description,
            color=colors["red"]
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild, member):
        """guild thingos """
        channel = self.bot.get_channel(guild.system_channel)
        db.execute("INSERT OR IGNORE INTO Guilds (GuildID) VALUES(?)", guild.id,)
        await channel.send("Thank you for inviting me to the server")
        await channel.send("Please do ~help to get started")
        await channel.send("also if edoC fails it is because your servers guildID didn't get put into the database please contact the dev about it \n*(you can find him in ~info)")
        annoy = member

    # async def update_db(self):
    #    members = self.bot.get_all_members()
    #    for member in members:
    #        db.execute("INSERT OR IGNORE INTO User (UserID) VALUES (?)", member.id)
    #    for server in self.bot.guilds:
    #        print(server.name)
    #        admins = None  # {}
    #        # `for member in guild.members:
    #        #    if
    #        #            admins += members
    #        # inthings = [server.id, self.config["default_prefix"], server.name, admins] #
    #        db.execute("INSERT OR IGNORE INTO guilds (GuildID, Prefix, GuildName, GuildAdmins) VALUES (?, ?, ?, ?);",
    #                   (server.id, self.config["default_prefix"], server.name, admins))
    #    db.commit()
    #    print("updated db")
    #    await asyncio.sleep(21600.0)

    def update_db(self):
        for member in self.allmembers:
            if member.bot:
                continue
            db.execute("INSERT OR IGNORE INTO User (UserID) VALUES (?)", member.id)

        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID, Prefix, GuildName) VALUES (?, ?, ?)",
                     ((guild.id, self.config["default_prefix"], guild.name,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO User (UserID) VALUES (?)",
                     ((member.id,) for member in self.allmembers if not member.bot))

        to_remove = []
        allmembers = self.bot.get_all_members()
        stored_members = db.column("SELECT UserID FROM User")
        for id_ in stored_members:
            if id_ not in list(allmembers):
                to_remove.append(id_)
        db.multiexec("DELETE FROM User WHERE UserID = ?",
                     ((id_,) for id_ in to_remove))

        db.commit()
        print("updated db")

    # async def update_db(self):
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
            await self.erroremb(ctx,
                                description=f'The command you have requested is not found. \nPlease make sure you typed it out right', )

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
            await self.erroremb(ctx=ctx,
                                description="You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await self.erroremb(ctx=ctx,
                                description=f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        else:
            print('Unknown error!')
            await self.erroremb(ctx, description="Sorry but this is an unknown error the devs has been notified!")
            await self.critlogschannel.send(
                f"{ctx.message.author.mention} [in {ctx.message.guild.id}, #{ctx.message.channel}] made an error typing a command. The error is unknown!")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        db.execute("DELETE FROM Guilds WHERE GuildID=?", (guild.id,))
        print(f"edoc has left {guild.name} it had {len(guild.members)} members")
        # todo add a thing to remove said guild from the database after an hour

    @commands.Cog.listener()
    async def on_member_join(self, guild, member):
        channel = self.bot.get_channel(guild.system_channel.id)
        if not self.config[f"join_message"]:
            return
        else:
            join_msg = self.config[f"join_message"]
            await channel.send(f"{join_msg} {member.mention}")

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
            logging.info(f'{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}')
        except AttributeError:
            print(f"Private message > {ctx.author} > {ctx.message.clean_content} > Blocked {blocked}")
            logging.info(f'Private message > ')
            # {ctx.author} > {ctx.message.clean_content}

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        global to_send
        logschannel = self.bot.get_channel(self.config["edoc_non_critical_logs"])
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
            totalmembers = sum(g.member_count for g in self.bot.guilds)

            await self.bot.change_presence(
                activity=discord.Game(
                    type=activity_type.get(activity, 2), name=f"Watching over {totalmembers} members!"
                ),
                status=status_type.get(status, discord.Status.online)
            )
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
                try:
                    invite_link = await to_send.create_invite(max_uses=1, unique=False, temporary=True)
                except discord.Forbidden:
                    invite_link = "Invalid perms"
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
    async def on_user_update(self, before, after):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        if before.name != after.name:
            embed = discord.Embed(title="Username change",
                                  colour=after.colour,
                                  timestamp=datetime.utcnow())

            fields = [("Before", before.name, False),
                      ("After", after.name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = discord.Embed(title="Discriminator change",
                                  colour=after.colour,
                                  timestamp=datetime.utcnow())

            fields = [("Before", before.discriminator, False),
                      ("After", after.discriminator, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = discord.Embed(title="Avatar change",
                                  description="New image is below, old to the right.",
                                  colour=blue,
                                  timestamp=datetime.utcnow())

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await noncritlogschannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        if before.display_name != after.display_name:
            embed = discord.Embed(title="Nickname change",
                                  colour=after.colour,
                                  timestamp=datetime.utcnow())

            fields = [("Before", before.display_name, False),
                      ("After", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

        elif before.roles != after.roles:
            embed = discord.Embed(title="Role updates",
                                  colour=after.colour,
                                  timestamp=datetime.utcnow())

            fields = [("Before", ", ".join([r.mention for r in before.roles]), False),
                      ("After", ", ".join([r.mention for r in after.roles]), False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        if not after.author.bot:
            if before.content != after.content:
                embed = discord.Embed(title="Message edit",
                                      description=f"Edit by {after.author.display_name}.",
                                      colour=after.author.colour,
                                      timestamp=datetime.utcnow())

                fields = [("Before", before.content, False),
                          ("After", after.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await noncritlogschannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        if not message.author.bot:
            embed = discord.Embed(title="Message deletion",
                                  description=f"Action by {message.author.display_name}.",
                                  colour=message.author.colour,
                                  timestamp=datetime.utcnow())

            fields = [("Content", message.content, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await noncritlogschannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, prev, cur):
        noncritlogschannel = self.bot.get_channel(self.noncritlogschannel)
        user = f"{member.name}#{member.discriminator}"
        if cur.afk and not prev.afk:
            await noncritlogschannel.send(f"{user} went AFK!")
        elif prev.afk and not cur.afk:
            await noncritlogschannel.send(f"{user} is no longer AFK!")
        elif cur.self_mute and not prev.self_mute:  # Would work in a push to talk channel
            await noncritlogschannel.send(f"{user} stopped talking!")
        elif prev.self_mute and not cur.self_mute:  # As would this one
            await noncritlogschannel.send(f"{user} started talking!")

    @commands.Cog.listener()
    async def premium_guild_subscription(self, ctx):
        await ctx.send(f"{ctx.auther} just boosted the server :party:")


def setup(bot):
    bot.add_cog(Events(bot))
