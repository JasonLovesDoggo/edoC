# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import argparse
import asyncio
import copy
import datetime
import logging
import re
import shlex
from collections import Counter
from io import BytesIO

import discord
from discord import NotFound, Object
from discord.ext import commands
from discord.ext.commands import Converter, BadArgument
from discord.utils import find

from cogs.Discordinfo import format_relative, plural
# from lib.db import db
from utils import checks, default
from utils.checks import MemberConverterr
from utils.default import mod_or_permissions
from utils.vars import *

log = logging.getLogger('mod')


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


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


async def Get_Banned_Users(bot):
    bans = bot.db.field("SELECT id FROM users WHERE banned = ?", "True")
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
    ctx.bot.db.execute("INSERT INTO users (?, ?)", (userid, reason,))
    # db.execute("INSERT INTO users (Reason)", reason)
    ctx.bot.db.commit()
    return await ctx.send(f'{userid} Was banned from using the bot')


def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role

class NoMuteRole(commands.CommandError):
    def __init__(self):
        super().__init__('This server does not have a mute role set up.')

def can_mute():
    async def predicate(ctx):
        is_owner = await ctx.bot.is_owner(ctx.author)
        if ctx.guild is None:
            return False

        if not ctx.author.guild_permissions.manage_roles and not is_owner:
            return False

        # This will only be used within this cog.

        role = discord.utils.get(ctx.guild.roles, name='Muted')
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(send_messages=False,
                                                                                      add_reactions=False))
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(speak=False))
        if role is None:
            perms = ctx.guild.default_role.permissions
            role = await ctx.guild.create_role(name="Muted", permissions=perms)
        return ctx.author.top_role > role
    return commands.check(predicate)

class Mod(commands.Cog, description='Moderator go brrrrrrrr ~ban'):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    async def _basic_cleanup_strategy(self, ctx, search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me and not (msg.mentions or msg.role_mentions):
                await msg.delete()
                count += 1
        return {'Bot': count}

    async def _complex_cleanup_strategy(self, ctx, search):
        prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild))  # thanks startswith todo update this bc it wont work rn

        def check(m):
            return m.author == ctx.me or m.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    async def _regular_user_cleanup_strategy(self, ctx, search):
        prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild))

        def check(m):
            return (m.author == ctx.me or m.content.startswith(prefixes)) and not (m.mentions or m.role_mentions)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @commands.command()
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.
        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.
        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.
        Members with Manage Messages can search up to 1000 messages.
        Members without can search up to 25 messages.
        """

        strategy = self._basic_cleanup_strategy
        is_mod = ctx.channel.permissions_for(ctx.author).manage_messages
        if ctx.channel.permissions_for(ctx.me).manage_messages:
            if is_mod:
                strategy = self._complex_cleanup_strategy
            else:
                strategy = self._regular_user_cleanup_strategy

        if is_mod:
            search = min(max(2, search), 1000)
        else:
            search = min(max(2, search), 25)

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

        await ctx.send('\n'.join(messages), delete_after=10)

    @commands.command(aliases=['newmembers', 'nu'])
    @commands.guild_only()
    async def newusers(self, ctx, *, count=5):
        """Tells you the newest members of the server.
        This is useful to check if any suspicious members have
        joined.
        The count parameter can only be up to 25.
        """
        count = max(min(count, 25), 5)

        if not ctx.guild.chunked:
            members = await ctx.guild.chunk(cache=True)

        members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:count]

        e = discord.Embed(title='New Members', colour=green)

        for member in members:
            body = f'Joined {format_relative(member.joined_at)}\nCreated {format_relative(member.created_at)}'
            e.add_field(name=f'{member} (ID: {member.id})', value=body, inline=False)

        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_emojis=True)
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
    @mod_or_permissions(kick_members=True)
    async def kick(self, ctx, member: MemberConverterr, *, reason: ActionReason = None):
        """Kicks a member from the server.
        In order for this to work, the bot must have Kick Member permissions.
        To use this command you must have Kick Members permission.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.kick(member, reason=reason)
        await ctx.send('\N{OK HAND SIGN}')

    # @commands.command(name="delprofanity", aliases=["delswears", "delcurses"])
    # @commands.guild_only
    # @commands.has_permissions(manage_guild=True)
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
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: MemberConverterr, *, name: str = None):
        """ Nicknames a user from the current server. """
        if await checks.check_priv(ctx, member):
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
    @commands.has_permissions(manage_nicknames=True)
    async def massnickname(self, ctx, *, name: str = None):
        """ Nicknames all the users from the current server. """
        for member in ctx.guild.members:
            if await checks.check_priv(ctx, member):
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
    @mod_or_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Bans a member from the server.
        You can also ban from ID to ban regardless whether they're
        in the server or not.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permission.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.ban(member, reason=reason)
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.guild_only()
    @mod_or_permissions(ban_members=True)
    async def multiban(self, ctx, members: commands.Greedy[MemberID], *, reason: ActionReason = None):
        """Bans multiple members from the server.
        This only works through banning via ID.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permission.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        total_members = len(members)
        if total_members == 0:
            return await ctx.send('Missing members to ban.')

        confirm = await ctx.prompt(f'This will ban **{plural(total_members):member}**. Are you sure?', reacquire=False)
        if not confirm:
            return await ctx.send('Aborting.')

        failed = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                failed += 1

        await ctx.send(f'Banned {total_members - failed}/{total_members} members.')

    @commands.command()
    @commands.guild_only()
    @mod_or_permissions(kick_members=True)
    async def softban(self, ctx, member: MemberID, *, reason: ActionReason = None):
        """Soft bans a member from the server.
        A softban is basically banning the member from the server but
        then unbanning the member as well. This allows you to essentially
        kick the member while removing their messages.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Kick Members permissions.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.ban(member, reason=reason)
        await ctx.guild.unban(member, reason=reason)
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    @commands.guild_only()
    @mod_or_permissions(ban_members=True)
    async def massban(self, ctx, *, args):
        """Mass bans multiple members from the server.
        This command has a powerful "command line" syntax. To use this command
        you and the bot must both have Ban Members permission. **Every option is optional.**
        Users are only banned **if and only if** all conditions are met.
        The following options are valid.
        `--channel` or `-c`: Channel to search for message history.
        `--reason` or `-r`: The reason for the ban.
        `--regex`: Regex that usernames must match.
        `--created`: Matches users whose accounts were created less than specified minutes ago.
        `--joined`: Matches users that joined less than specified minutes ago.
        `--joined-before`: Matches users who joined before the member ID given.
        `--joined-after`: Matches users who joined after the member ID given.
        `--no-avatar`: Matches users who have no avatar. (no arguments)
        `--no-roles`: Matches users that have no role. (no arguments)
        `--show`: Show members instead of banning them (no arguments).
        Message history filters (Requires `--channel`):
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--match`: A regex to match the message content to.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.
        `--files`: Checks if the message has attachments (no arguments).
        `--embeds`: Checks if the message has embeds (no arguments).
        """

        # For some reason there are cases due to caching that ctx.author
        # can be a User even in a guild only context
        # Rather than trying to work out the kink with it
        # Just upgrade the member itself.
        if not isinstance(ctx.author, MemberConverterr):
            try:
                author = await ctx.guild.fetch_member(ctx.author.id)
            except discord.HTTPException:
                return await ctx.send('Somehow, Discord does not seem to think you are in this server.')
        else:
            author = ctx.author

        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--channel', '-c')
        parser.add_argument('--reason', '-r')
        parser.add_argument('--search', type=int, default=100)
        parser.add_argument('--regex')
        parser.add_argument('--no-avatar', action='store_true')
        parser.add_argument('--no-roles', action='store_true')
        parser.add_argument('--created', type=int)
        parser.add_argument('--joined', type=int)
        parser.add_argument('--joined-before', type=int)
        parser.add_argument('--joined-after', type=int)
        parser.add_argument('--contains')
        parser.add_argument('--starts')
        parser.add_argument('--ends')
        parser.add_argument('--match')
        parser.add_argument('--show', action='store_true')
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            return await ctx.send(str(e))

        members = []

        if args.channel:
            channel = await commands.TextChannelConverter().convert(ctx, args.channel)
            before = args.before and discord.Object(id=args.before)
            after = args.after and discord.Object(id=args.after)
            predicates = []
            if args.contains:
                predicates.append(lambda m: args.contains in m.content)
            if args.starts:
                predicates.append(lambda m: m.content.startswith(args.starts))
            if args.ends:
                predicates.append(lambda m: m.content.endswith(args.ends))
            if args.match:
                try:
                    _match = re.compile(args.match)
                except re.error as e:
                    return await ctx.send(f'Invalid regex passed to `--match`: {e}')
                else:
                    predicates.append(lambda m, x=_match: x.match(m.content))
            if args.embeds:
                predicates.append(args.embeds)
            if args.files:
                predicates.append(args.files)

            async for message in channel.history(limit=min(max(1, args.search), 2000), before=before, after=after):
                if all(p(message) for p in predicates):
                    members.append(message.author)
        else:
            if ctx.guild.chunked:
                members = ctx.guild.members
            else:
                async with ctx.typing():
                    await ctx.guild.chunk(cache=True)
                members = ctx.guild.members

        # member filters
        predicates = [
            lambda m: isinstance(m, MemberConverterr) and can_execute_action(ctx, author, m),  # Only if applicable
            lambda m: not m.bot,  # No bots
            lambda m: m.discriminator != '0000',  # No deleted users
        ]

        converter = commands.MemberConverter()

        if args.regex:
            try:
                _regex = re.compile(args.regex)
            except re.error as e:
                return await ctx.send(f'Invalid regex passed to `--regex`: {e}')
            else:
                predicates.append(lambda m, x=_regex: x.match(m.name))

        if args.no_avatar:
            predicates.append(lambda m: m.avatar == m.default_avatar)
        if args.no_roles:
            predicates.append(lambda m: len(getattr(m, 'roles', [])) <= 1)

        now = discord.utils.utcnow()
        if args.created:
            def created(member, *, offset=now - datetime.timedelta(minutes=args.created)):
                return member.created_at > offset

            predicates.append(created)
        if args.joined:
            def joined(member, *, offset=now - datetime.timedelta(minutes=args.joined)):
                if isinstance(member, discord.User):
                    # If the member is a user then they left already
                    return True
                return member.joined_at and member.joined_at > offset

            predicates.append(joined)
        if args.joined_after:
            _joined_after_member = await converter.convert(ctx, str(args.joined_after))

            def joined_after(member, *, _other=_joined_after_member):
                return member.joined_at and _other.joined_at and member.joined_at > _other.joined_at

            predicates.append(joined_after)
        if args.joined_before:
            _joined_before_member = await converter.convert(ctx, str(args.joined_before))

            def joined_before(member, *, _other=_joined_before_member):
                return member.joined_at and _other.joined_at and member.joined_at < _other.joined_at

            predicates.append(joined_before)

        members = {m for m in members if all(p(m) for p in predicates)}
        if len(members) == 0:
            return await ctx.send('No members found matching criteria.')

        if args.show:
            members = sorted(members, key=lambda m: m.joined_at or now)
            fmt = "\n".join(f'{m.id}\tJoined: {m.joined_at}\tCreated: {m.created_at}\t{m}' for m in members)
            content = f'Current Time: {discord.utils.utcnow()}\nTotal members: {len(members)}\n{fmt}'
            file = discord.File(BytesIO(content.encode('utf-8')), filename='members.txt')
            return await ctx.send(file=file)

        if args.reason is None:
            return await ctx.send('--reason flag is required.')
        else:
            reason = await ActionReason().convert(ctx, args.reason)

        confirm = await ctx.prompt(f'This will ban **{plural(len(members)):member}**. Are you sure?')
        if not confirm:
            return await ctx.send('Aborting.')

        count = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                pass
            else:
                count += 1

        await ctx.send(f'Banned {count}/{len(members)}')

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def massunban(self, ctx, *members: MemberID):
        """ Mass unbans multiple members from the server. """
        try:
            for member_id in members:
                await ctx.guild.unban(discord.Object(id=str(member_id)))
            await ctx.send(default.actionmessage("massunbans", mass=True))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    async def masskick(self, ctx, reason: ActionReason, *members: MemberID):
        """ Mass kicks multiple members from the server. """
        try:
            for member_id in members:
                await ctx.guild.kick(discord.Object(id=str(member_id)), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("masskickd", mass=True))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: MemberID, *, reason: str = None):
        """ Unbans a user from the current server. """
        try:
            await ctx.guild.unban(discord.Object(id=str(member)), reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("unbanned"))
        except Exception as e:
            await ctx.send(e)

    @commands.group(invoke_without_command=True)
    @can_mute()
    async def mute(self, ctx, members: commands.Greedy[discord.Member], *, reason: ActionReason = None):
        """Mutes members using the configured mute role.
       The bot must have Manage Roles permission and be
       above the muted role in the hierarchy.
       To use this command you need to be higher than the
       mute role in the hierarchy and have Manage Roles
           permission at the server level."""
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
        guild = ctx.guild
        total = len(members)
        if total == 0:
            return await ctx.warn('Missing members to mute.')
        elif total > 20:
            return await ctx.error('You may only mute 20 people at a time')
        role = discord.utils.get(guild.roles, name='Muted')
        failed = 0
        em = discord.Embed(colour=invis, description='')
        for member in members:
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason=reason)
                    em.description += f'{self.bot.icons["greenTick"]} {member.name} Sucsessfully muted'
                except discord.HTTPException:
                    failed += 1
                    em.description += f'{self.bot.icons["RedTick"]} {member.name} Failed to mute muted'
        em.set_footer(text=f'Muted [{total - failed}/{total}]')
        await ctx.try_reply(embed=em)

    """"# Mute a Member
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
    @commands.is_owner()
    async def do(self, ctx, times: int, *, command):
        """Repeats a command a specified number of times."""
        msg = copy.copy(ctx.message)
        msg.content = ctx.prefix + command

        new_ctx = await self.bot.get_context(msg, cls=type(ctx))

        for i in range(times):
            await new_ctx.reinvoke()

    #@commands.group(name='mute', invoke_without_command=True)
    #@can_mute()
    #async def _mute(self, ctx, members: commands.Greedy[MemberConverterr], *, reason: ActionReason = None):
    #    """Mutes members using the configured mute role.
    #    The bot must have Manage Roles permission and be
    #    above the muted role in the hierarchy.
    #    To use this command you need to be higher than the
    #    mute role in the hierarchy and have Manage Roles
    #    permission at the server level.
    #    """
#
    #    if reason is None:
    #        reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
#
    #    role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)
    #    total = len(members)
    #    if total == 0:
    #        return await ctx.send('Missing members to mute.')
#
    #    failed = 0
    #    for member in members:
    #        try:
    #            await member.add_roles(role, reason=reason)
    #        except discord.HTTPException:
    #            failed += 1
#
    #    if failed == 0:
    #        await ctx.send('\N{THUMBS UP SIGN}')
    #    else:
    #        await ctx.send(f'Muted [{total - failed}/{total}]')
#
    @commands.command(name='unmute')
    @can_mute()
    async def _unmute(self, ctx, members: commands.Greedy[MemberConverterr], *, reason: ActionReason = None):
        """Unmutes members using the configured mute role.
        The bot must have Manage Roles permission and be
        above the muted role in the hierarchy.
        To use this command you need to be higher than the
        mute role in the hierarchy and have Manage Roles
        permission at the server level.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)
        total = len(members)
        if total == 0:
            return await ctx.send('Missing members to unmute.')

        failed = 0
        for member in members:
            try:
                await member.remove_roles(role, reason=reason)
            except discord.HTTPException:
                failed += 1

        if failed == 0:
            await ctx.send('\N{THUMBS UP SIGN}')
        else:
            await ctx.send(f'Unmuted [{total - failed}/{total}]')

    @commands.command(aliases=["ar"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def announcerole(self, ctx, *, role: discord.Role):
        """ Makes a role mentionable and removes it whenever you mention the role """
        if role == ctx.guild.default_role:
            return await ctx.warn("To prevent abuse, I won't allow mentionable role for everyone/here role.")

        if ctx.author.top_role.position <= role.position:
            return await ctx.warn(
                "It seems like the role you attempt to mention is over your permissions, therefore I won't allow you.")

        if ctx.me.top_role.position <= role.position:
            return await ctx.error("This role is above my permissions, I can't make it mentionable ;-;")

        await role.edit(mentionable=True, reason=f"[ {ctx.author} ] announcerole command")
        msg = await ctx.success(
            f"**{role.name}** is now mentionable, if you don't mention it within 30 seconds, I will revert the changes.")

        while True:
            def role_checker(m):
                if role.mention in m.content:
                    return True
                return False

            try:
                checker = await self.bot.wait_for("message", timeout=30.0, check=role_checker)
                if checker.author.id == ctx.author.id:
                    await role.edit(mentionable=False, reason=f"[ {ctx.author} ] announcerole command")
                    return await msg.edit(
                        content=f"**{role.name}** mentioned by **{ctx.author}** in {checker.channel.mention}")

                else:
                    await checker.delete()
            except asyncio.TimeoutError:
                await role.edit(mentionable=False, reason=f"[ {ctx.author} ] announcerole command")
                return await msg.edit(content=f"**{role.name}** was never mentioned by **{ctx.author}**...")

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
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
    @commands.has_permissions(manage_roles=True)
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
    @commands.has_permissions(manage_roles=True)
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
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx):
        """ Removes messages from the current server. """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            await ctx.send(f'Successfully removed {deleted} messages.', delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

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
    async def user(self, ctx, member: MemberConverterr, search=100):
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

    @prune.command(name="bot", aliases=['bots'])
    async def _bots(self, ctx, prefix, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""


        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or m.content.startswith(tuple(prefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="users")
    async def _users(self, ctx, search=100):
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

    @prune.command()
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.
        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.
        The messages are only deleted if all options are met unless
        the `--or` flag is passed, in which case only if any is met.
        The following options are valid.
        `--user`: A mention or name of the user to remove.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.
        Flag options (no arguments):
        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any
        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        if args.after:
            if args.search is None:
                args.search = 2000

        if args.search is None:
            args.search = 100

        args.search = max(0, min(2000, args.search)) # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)

    # Mute related stuff

    async def update_mute_role(self, ctx, config, role, *, merge=False):
        guild = ctx.guild
        if config and merge:
            members = config.muted_members
            # If the roles are being merged then the old members should get the new role
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id}): Merging mute roles'
            async for member in self.bot.resolve_member_ids(guild, members):
                if not member._roles.has(role.id):
                    try:
                        await member.add_roles(role, reason=reason)
                    except discord.HTTPException:
                        pass
        else:
            members = set()

        members.update(map(lambda m: m.id, role.members))
        #query = """INSERT INTO guild_mod_config (id, mute_role_id, muted_members)
        #           VALUES ($1, $2, $3::bigint[]) ON CONFLICT (id)
        #           DO UPDATE SET
        #               mute_role_id = EXCLUDED.mute_role_id,
        #               muted_members = EXCLUDED.muted_members
        #        """
        #await self.bot.pool.execute(query, guild.id, role.id, list(members))
        #self.get_guild_config.invalidate(self, guild.id)

def setup(bot):
    bot.add_cog(Mod(bot))
