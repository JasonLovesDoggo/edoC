import logging

from discord.utils import find

from discord import NotFound, Object

import discord
import re
import asyncio
from discord.ext import commands
from discord.ext.commands import converter, Converter, BadArgument
from utils import permissions, default
from utils.data import get_prefix
from lib.db import db
from utils.gets import getChannel
from utils.vars import *
from utils.default import send
log = logging.getLogger('LOG')

class BannedUser(Converter):
    async def convert(self, ctx, arg):
        if ctx.guild.me.guild_permissions.ban_members:
            if arg.isdigit():
                try:
                    return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
                except NotFound:
                    raise BadArgument

        banned = [e.user for e in await ctx.guild.bans()]
        if banned:
            if (user := find(lambda u: str(u) == arg, banned)) is not None:
                return user
            else:
                raise BadArgument


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f"reason is too long ({len(argument)}/{reason_max})")
        return ret


BannedUsers = {}


async def Get_Banned_Users():
    bans = db.field("SELECT UserID FROM users WHERE Banned = ?", "True")
    for UserID in bans:
        BannedUsers + UserID


async def BannedU(ctx):
    if ctx.author in BannedUsers:
        print(f"Command by {ctx.author} blocked!")

    async def pred(ctx):
        if ctx.author in BannedUsers:
            return ctx.send("You are banned from using commands")
    return pred


async def BanUser(ctx, userid: MemberID, reason):
    BannedUsers + userid
    db.execute("INSERT INTO users (?, ?)", userid, reason)
    # db.execute("INSERT INTO users (Reason)", reason)
    db.commit()
    return await ctx.send(userid + " Was banned from using the bot")


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.prefix = get_prefix

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_emojis=True)
    async def emoji(self, ctx, emoji: discord.PartialEmoji, *roles: discord.Role):
        """This clones a specified emoji that only specified roles
        are allowed to use.
        """
        # fetch the emoji asset and read it as bytes.
        emoji_bytes = await emoji.read()

        # the key parameter here is `roles`, which controls
        # what roles are able to use the emoji.
        await ctx.guild.create_custom_emoji(
            name=emoji.name,
            image=emoji_bytes,
            roles=roles,
            reason='Very secret business.'
        )

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """ Kicks a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        try:
            await member.kick(reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("kicked"))
        except Exception as e:
            await ctx.send(e)

    # @commands.command(name="delprofanity", aliases=["delswears", "delcurses"])
    # @commands.guild_only
    # @permissions.has_permissions(manage_guild=True)
    # async def remove_profanity(self, ctx, *words):
    #    with open("./data/profanity.txt", "r", encoding="utf-8") as f:
    #        stored = [w.strip() for w in f.readlines()]
    #
    #    with open("./data/profanity.txt", "w", encoding="utf-8") as f:
    #        f.write("".join([f"{w}\n" for w in stored if w not in words]))
    #
    #    profanity.load_censor_words_from_file("./data/profanity.txt")
    #    await ctx.send("Action complete.")
    #    await ctx.send("Action complete.")
    @commands.command(aliases=["nick"])
    @commands.guild_only()
    @permissions.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, name: str = None):
        """ Nicknames a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        try:
            await member.edit(nick=name, reason=default.responsible(ctx.author, "Changed by command"))
            message = f"Changed **{member.name}'s** nickname to **{name}**"
            if name is None:
                message = f"Reset **{member.name}'s** nickname"
            await ctx.send(message)
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=["massnick"])
    @commands.guild_only()
    @permissions.has_permissions(manage_nicknames=True)
    async def massnickname(self, ctx, *, name: str = None):
        """ Nicknames all the users from the current server. """
        for member in ctx.guild.members:
            if await permissions.check_priv(ctx, member):
                return
            else:
                if member.id == 845186772698923029 or 511724576674414600:
                    continue
                else:
                    try:
                        await member.edit(nick=name, reason=default.responsible(ctx.author, "Changed by command"))
                        message = f"Changed **{member.name}'s** nickname to **{name}**"
                        if name is None:
                            message = f"Reset **{member.name}'s** nickname"
                        await ctx.send(message)
                    except Exception as e:
                        await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: str = None):
        """ Bans a user from the current server. """
        m = ctx.guild.get_member(member)
        if m is not None and await permissions.check_priv(ctx, m):
            return

        try:
            await ctx.guild.ban(discord.Object(id=member), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("banned"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @permissions.has_permissions(ban_members=True)
    async def massban(self, ctx, reason: ActionReason, *members: MemberID):
        """ Mass bans multiple members from the server. """
        try:
            for member_id in members:
                await ctx.guild.ban(discord.Object(id=member_id), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("massbans", mass=True))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @permissions.has_permissions(ban_members=True)
    async def massunban(self, ctx, *members: MemberID):
        """ Mass unbans multiple members from the server. """
        try:
            for member_id in members:
                await ctx.guild.unban(discord.Object(id=member_id))
            await ctx.send(default.actionmessage("massunbans", mass=True))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @permissions.has_permissions(kick_members=True)
    async def masskick(self, ctx, reason: ActionReason, *members: MemberID):
        """ Mass kicks multiple members from the server. """
        try:
            for member_id in members:
                await ctx.guild.kick(discord.Object(id=member_id), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("masskickd", mass=True))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def unban(self, ctx, member: MemberID, *, reason: str = None):
        """ Unbans a user from the current server. """
        try:
            await ctx.guild.unban(discord.Object(id=member), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("unbanned"))
        except Exception as e:
            await ctx.send(e)

    """    # Mute a Member
    @commands.command(aliases=['Mute'])
    @commands.has_permissions(manage_roles=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def mute(self, ctx, mem: str):
        member = getUser(ctx, mem)
        if member:
            if not utils.find(lambda r: "mute" in r.name.lower(), ctx.message.guild.roles):
                if not utils.find(lambda r: "Muted" == r.name, ctx.message.guild.roles):
                    perms = utils.find(lambda r: "@everyone" == r.name, ctx.message.guild.roles).permissions
                    role = await ctx.guild.create_role(name="Muted", permissions=perms)
                    log.info('Created role: Muted')
                    for channel in ctx.guild.text_channels:
                        await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(send_messages=False, add_reactions=False))
                    for channel in ctx.guild.voice_channels:
                        await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(speak=False))
                    log.info('Prepared Mute role for mutes in channels')
                role = utils.find(lambda r: "Muted" == r.name, ctx.message.guild.roles)
            else:
                role = utils.find(lambda r: "mute" in r.name.lower(), ctx.message.guild.roles)

            if role not in member.roles:
                roles = member.roles
                roles.append(role)
                asyncio.sleep(0.5)
                await member.edit(roles=roles)
                log.info(f'Muted {member}')

                e = discord.Embed(color=embedColor(self))
                e.set_author(name="\N{SPEAKER WITH CANCELLATION STROKE} Muted " + str(member))
                await edit(ctx, embed=e)
            else:
                await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Already muted", ttl=5)

    # Mute a Member
    @commands.command(aliases=['Unmute'])
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx, mem: str):
        member = getUser(ctx, mem)
        if member:
            role = utils.find(lambda r: "mute" in r.name.lower(), member.roles)
            if role:
                roles = member.roles
                roles.remove(role)
                asyncio.sleep(0.5)
                await member.edit(roles=roles)
                log.info(f'Unmuted {member}')

                e = discord.Embed(color=embedColor(self))
                e.set_author(name="\N{SPEAKER} Unmuted " + str(member))
                await edit(ctx, embed=e)
            else:
                await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Member is not muted", ttl=5)
                
                    # SoftBan a Member (ban, delelte messagea and unban)
    @commands.command(aliases=['Softban'])
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def softban(self, ctx, member: str, *, reason: str=None):
        Softban a Member(Kick and delete Messages
        member = getUser(ctx, member)
        if member:
            try:
                await ctx.guild.ban(member, reason=reason)
                await ctx.guild.unban(member)
            except discord.Forbidden:
                await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Missing permissions to ban this Member", ttl=5)
            except discord.HTTPException:
                await edit(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Something went wrong while trying to ban...", ttl=5)
            else:
                e = discord.Embed(color=embedColor(self))
                e.set_author(icon_url="https://cdn.discordapp.com/attachments/278603491520544768/301087009408024580/273910007857414147.png",
                             name="Soft Banned: " + str(member))
                await edit(ctx, embed=e)"""
    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Mutes a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        muted_role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            return await ctx.send(
                "Are you sure you've made a role called **Muted**? Remember that it's case sensitive too...")

        try:
            await member.add_roles(muted_role, reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("muted"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Unmutes a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        muted_role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            return await ctx.send(
                "Are you sure you've made a role called **Muted**? Remember that it's case sensitive too...")

        try:
            await member.remove_roles(muted_role, reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("unmuted"))
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=["ar"])
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def announcerole(self, ctx, *, role: discord.Role):
        """ Makes a role mentionable and removes it whenever you mention the role """
        if role == ctx.guild.default_role:
            return await ctx.send("To prevent abuse, I won't allow mentionable role for everyone/here role.")

        if ctx.author.top_role.position <= role.position:
            return await ctx.send(
                "It seems like the role you attempt to mention is over your permissions, therefore I won't allow you.")

        if ctx.me.top_role.position <= role.position:
            return await ctx.send("This role is above my permissions, I can't make it mentionable ;-;")

        await role.edit(mentionable=True, reason=f"[ {ctx.author} ] announcerole command")
        msg = await ctx.send(
            f"**{role.name}** is now mentionable, if you don't mention it within 30 seconds, I will revert the changes.")

        while True:
            def role_checker(m):
                if (role.mention in m.content):
                    return True
                return False

            try:
                checker = await self.bot.wait_for("message", timeout=30.0, check=role_checker)
                if checker.author.id == ctx.author.id:
                    await role.edit(mentionable=False, reason=f"[ {ctx.author} ] announcerole command")
                    return await msg.edit(
                        content=f"**{role.name}** mentioned by **{ctx.author}** in {checker.channel.mention}")
                    break
                else:
                    await checker.delete()
            except asyncio.TimeoutError:
                await role.edit(mentionable=False, reason=f"[ {ctx.author} ] announcerole command")
                return await msg.edit(content=f"**{role.name}** was never mentioned by **{ctx.author}**...")
                break

    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def find(self, ctx):
        """ Finds a user within your search term """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @find.command(name="playing")
    async def find_playing(self, ctx, *, search: str):
        loop = []
        for i in ctx.guild.members:
            if i.activities and (not i.bot):
                for g in i.activities:
                    if g.name and (search.lower() in g.name.lower()):
                        loop.append(f"{i} | {type(g).__name__}: {g.name} ({i.id})")

        await default.prettyResults(
            ctx, "playing", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="username", aliases=["name"])
    async def find_name(self, ctx, *, search: str):
        loop = [f"{i} ({i.id})" for i in ctx.guild.members if search.lower() in i.name.lower() and not i.bot]
        await default.prettyResults(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="nickname", aliases=["nick"])
    async def find_nickname(self, ctx, *, search: str):
        loop = [f"{i.nick} | {i} ({i.id})" for i in ctx.guild.members if i.nick if
                (search.lower() in i.nick.lower()) and not i.bot]
        await default.prettyResults(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="id")
    async def find_id(self, ctx, *, search: int):
        loop = [f"{i} | {i} ({i.id})" for i in ctx.guild.members if (str(search) in str(i.id)) and not i.bot]
        await default.prettyResults(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="discriminator", aliases=["discrim"])
    async def find_discriminator(self, ctx, *, search: str):
        if not len(search) == 4 or not re.compile("^[0-9]*$").search(search):
            return await ctx.send("You must provide exactly 4 digits")

        loop = [f"{i} ({i.id})" for i in ctx.guild.members if search == i.discriminator]
        await default.prettyResults(
            ctx, "discriminator", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def lock(self, ctx):
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if not overwrite.send_messages:
            embed = discord.Embed(colour=magenta,
                                  description=f"{channel.mention} is already a locked channel")
            embed.set_author(name='Invalid usage',
                             icon_url=picture("Warning"))
            try:
                await ctx.send(embed=embed)
                return
            except:
                try:
                    await ctx.author.send(embed=embed)
                    return
                except:
                    return
        embed = discord.Embed(colour=magenta,
                              description=f":lock: **Locked channel** {ctx.channel.mention}")
        await ctx.send(embed=embed)
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def unlock(self, ctx):
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages:
            embed = discord.Embed(colour=magenta,
                                  description=f"{channel.mention} is not a locked channel")
            embed.set_author(name='Invalid usage',
                             icon_url=picture("Warning"))
            try:
                await ctx.send(embed=embed)
                return
            except:
                try:
                    await ctx.author.send(embed=embed)
                    return
                except:
                    return
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(colour=0xFF004D,
                              description=f":unlock: **Unlocked channel** {ctx.channel.mention}")
        try:
            await ctx.send(embed=embed)
        except:
            try:

                await ctx.author.send(embed=embed)
            except:
                pass

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def cls(self, ctx, amount: int):
        amount2 = amount + 1
        await ctx.channel.purge(limit=amount2)

    @commands.group(aliases=["purge", "clr", "clear"])
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @permissions.has_permissions(manage_messages=True)
    async def prune(self, ctx):
        """ Removes messages from the current server. """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
        if limit > 2000:
            return await ctx.send(f"Too many messages to search given ({limit}/2000)")

        if not before:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.send(f"Error: {e} (try a smaller search?)")

        deleted = len(deleted)
        if message is True:
            await ctx.send(f"🚮 Successfully removed {deleted} message{'' if deleted == 1 else 's'}.", delete_after=1.0)
            await ctx.message.delete()

    @prune.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @prune.command()
    async def mentions(self, ctx, search=100):
        """Removes messages that have mentions in them."""
        await self.do_removal(ctx, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @prune.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @prune.command(name="all")
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @prune.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name="bots")
    async def _bots(self, ctx, search=100, prefix=None):
        """Removes a bot user's messages and messages with their optional prefix."""

        getprefix = self.prefix if prefix else self.config["prefix"]

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or m.content.startswith(tuple(getprefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="users")
    async def _users(self, ctx, prefix=None, search=100):
        """Removes only user messages. """

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="emojis")
    async def _emojis(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="reactions")
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f"Successfully removed {total_reactions} reactions.")


def setup(bot):
    bot.add_cog(Mod(bot))
