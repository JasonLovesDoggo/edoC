import os
from datetime import datetime
import logging
import psutil
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from discord.ext.commands import errors
from edoC.utils import default
from edoC.lib.db import db
import discord

owners = default.config()["owners"]


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ready = False
        self.config = default.config()
        self.process = psutil.Process(os.getpid())
        self.scheduler = AsyncIOScheduler()
        self.bot.normal_commands = 0
        self.bot.owner_commands = 0


    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
                     ((member.id,) for member in self.guild.members if not member.bot))
        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?",
                     ((id_,) for id_ in to_remove))

        db.commit()
        print("updated db")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

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
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, ctx, user):
        emb = discord.Embed(title=f"d",
                            color=0x04A4EC,
                            timestamp=ctx.message.created_at, )

        await ctx.send("Thank you for inviting me to the server")
        await ctx.send("Please do ~help to get started")
        guildid = ctx.guild.id
        changecmd = f'''INSERT INTO guilds (GuildId, Prefix, GuildName) values ('{guildid}', '{self.config["default_prefix"]}', '{ctx.guild.name}')'''
        #insert into products (name, price) values ('sprite', 9)
        db.execute(changecmd)
        annoy = user

    @commands.Cog.listener()
    async def on_guild_remove(self, ctx, guild):
        pass

    @commands.Cog.listener()
    async def on_member_join(self, guild, user):
        if not self.config[f"join_message"]:
            return

        try:
            to_send = sorted([chan for chan in guild.channels if
                              chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)],
                             key=lambda x: x.position)[0]
        except IndexError:
            pass
        else:
            join_msg = self.config[f"join_message"]
            await to_send.send(f"{join_msg} {user.mention}")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.normal_commands + 1
        if ctx.message.author.id in self.config[f"owners"]:
            self.bot.owner_commands + 1
        try:
            print(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")
            logging.basicConfig(filename="log.log",
                                format='%(asctime)s %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S %p',
                                level=logging.DEBUG,
                                filemode='w+')
            logging.info(f'{ctx.guild.name} > ')  # {ctx.author} > {ctx.message.clean_content}
        except AttributeError:
            print(f"Private message > {ctx.author} > {ctx.message.clean_content}")
            logging.info(f'Private message > ')
            # {ctx.author} > {ctx.message.clean_content}

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not self.ready:
            self.ready = True
            self.scheduler.start()
            self.update_db

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
            for x in self.bot.guilds:
                field = db.field("SELECT GuildId FROM 'guilds'")
                field2 = db.field("SELECT GuildName FROM 'guilds'")
                guilds[field2] = field
            for Server in self.bot.guilds:
                try:
                    to_send = sorted([chan for chan in Server.channels if
                                      chan.permissions_for(Server.me).send_messages and isinstance(chan,
                                                                                                   discord.TextChannel)],
                                     key=lambda x: x.position)[0]
                except IndexError:
                    pass
                else:
                    invite_link = await to_send.create_invite(max_uses=1, unique=False, temporary=True)
                if Server.id in guilds:
                    verified: bool = True
                else:
                    verified = False
                print(f"{Server} ~ {Server.owner} ~ {Server.member_count} ~ {invite_link} ~ System broken rn")
        else:
            print(f"{self.bot.user} Reconnected")
            logging.log("Bot reconnected")

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
