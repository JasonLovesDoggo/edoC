import unicodedata
from asyncio import sleep
from collections import Counter
from typing import Union

import discord

from io import BytesIO

from discord.utils import format_dt

from utils import default
from discord.ext import commands
from utils.vars import embedfooter, random_color
from utils.default import spacefill, Context


def format_relative(dt):
    return format_dt(dt, 'R')


def diff(num1, num2):
    if num1 > num2:
        answer = num1 - num2
    elif num2 > num1:
        answer = num2 - num1
    else:
        answer = 0
    return answer


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'


class Discord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour)
        avatar = member.avatar.with_static_format('png')
        e.set_author(name=str(member), icon_url=avatar)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').replace('guild', 'server').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name='Allowed', value='\n'.join(allowed))
        e.add_field(name='Denied', value='\n'.join(denied))
        await ctx.send(embed=e)

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

    @commands.command()
    async def avatar(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        """Shows a user's enlarged avatar (if possible)."""
        embed = discord.Embed(color=0x2F3136)
        user = user or ctx.author
        avatar = user.avatar.with_static_format('png')
        embed.set_author(name=str(user), url=avatar)
        embed.set_image(url=avatar)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx):
        """ Get all roles in current server """
        allroles = ""
        largest_name = 0
        most_members = 0

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            if len(role.name) > largest_name:
                largest_name = len(role.name)
            if len(role.members) > most_members:
                most_members = len(role.members)

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            numofroles = len(str(len(ctx.guild.roles)))
            length = len(role.name)
            allroles += f"[{str(num).zfill(numofroles)}] {role.id}\t{role.name}{spacefill(largest_name - length + 1)}[ Users: {len(role.members)}{spacefill(len(str(most_members - len(role.members))))}]\r\n"

        data = BytesIO(allroles.encode("utf-8"))
        await ctx.send(content=f"Roles in **{ctx.guild.name}**",
                       file=discord.File(data, filename=f"{default.CustomTimetext('apache', 'Roles')}"))

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, *, user: discord.Member = None):
        """ Check when a user joined the current server """
        user = user or ctx.author

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar.url)
        embed.description = f"**{user}** joined **{ctx.guild.name}**\n{default.date(user.joined_at)}"
        await ctx.send(embed=embed)

    @commands.command(aliases=["joinme", "inviteme", "botinvite"])
    async def invite(self, ctx):
        """Joins a server."""
        perms = discord.Permissions.all()
        await ctx.send(f'<{discord.utils.oauth_url(self.bot.client_id, permissions=perms)}>')

    @commands.command()
    @commands.guild_only()
    async def mods(self, ctx):
        """ Check which mods are online on current guild """
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"

        await ctx.send(f"Mods in **{ctx.guild.name}**\n{message}")

    @commands.command(aliases=['guildinfo'])
    @commands.guild_only()
    async def serverinfo(self, ctx, *, guild_id: int = None):
        """Shows info about the current server."""
        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(f'Invalid Guild ID given.')
        else:
            guild = ctx.guild

        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)

        # figure out what channels are 'secret'
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1
        e = discord.Embed(colour=0x2F3136)
        e.title = guild.name
        e.description = f'**ID**: {guild.id}\n**Owner**: {guild.owner}'
        if guild.icon:
            e.set_thumbnail(url=guild.icon.url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: '<:text_channel:879518927019966485>',
            discord.VoiceChannel: '<:voice_channel:879518950071869450>',
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f'{emoji} {total} ({secrets} locked)')
            else:
                channel_info.append(f'{emoji} {total}')

        info = []
        features = set(guild.features)
        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'COMMUNITY': 'Community Server',
            'FEATURABLE': 'Featured',
            'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner'
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'{ctx.tick(True)}: {label}')

        if info:
            e.add_field(name='Features', value='\n'.join(info))

        e.add_field(name='Channels', value='\n'.join(channel_info))

        if guild.premium_tier != 0:
            boosts = f'Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts'
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f'{boosts}\nLast Boost: {last_boost} ({format_relative(last_boost.premium_since)})'
            e.add_field(name='Boosts', value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        fmt = f'Total: {guild.member_count} ({plural(bots):bot})'

        e.add_field(name='Members', value=fmt, inline=False)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats['animated'] += 1
                emoji_stats['animated_disabled'] += not emoji.available
            else:
                emoji_stats['regular'] += 1
                emoji_stats['disabled'] += not emoji.available
                gel = guild.emoji_limit
                fmt = f'Regular: {emoji_stats["regular"]}/{gel}\nAnimated: {emoji_stats["animated"]}/{gel}\n'
                if emoji_stats['disabled'] or emoji_stats['animated_disabled']:
                    fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f'{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit * 2}'
        e.add_field(name='Emoji', value=fmt, inline=False)
        e.set_footer(text='Created').timestamp = guild.created_at
        await ctx.send(embed=e)

    # @server.command(name="avatar", aliases=["icon"])
    # async def server_avatar(self, ctx):
    #    """ Get the current server icon """
    #    if not ctx.guild.icon:
    #        return await ctx.send("This server does not have a avatar...")
    #    await ctx.send(
    #        embed=discord.Embed(description=f"Avatar of **{ctx.guild.name}**", ).set_image(url=ctx.guild.icon))

    # @server.command(name="banner")
    # async def server_banner(self, ctx):
    #    """ Get the current banner image """
    #    if not ctx.guild.banner:
    #        return await ctx.send("This server does not have a banner...")
    #    await ctx.send(f"Banner of **{ctx.guild.name}**\n{ctx.guild.banner}")

    @commands.command()
    async def info(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        """Shows info about a user."""

        user = user or ctx.author
        e = discord.Embed()
        roles = [role.name.replace('@', '@\u200b') for role in getattr(user, 'roles', []) if
                 not role.id == ctx.guild.default_role.id]

        e.set_author(name=str(user))
        join_position = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user) + 1

        def format_date(dt):
            if dt is None:
                return 'N/A'
            return f'{format_dt(dt, "F")} ({format_relative(dt)})'

        e.add_field(name='Join Position', value=join_position)
        e.add_field(name='ID', value=user.id, inline=False)
        e.add_field(name='Joined', value=format_date(getattr(user, 'joined_at', None)), inline=False)
        e.add_field(name='Created', value=format_date(user.created_at), inline=False)

        voice = getattr(user, 'voice', None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
            e.add_field(name='Voice', value=voice, inline=False)

        if roles:
            e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles',
                        inline=False)

        colour = user.colour
        if colour.value:
            e.colour = colour

        if user.avatar:
            e.set_thumbnail(url=user.avatar.url)

        if isinstance(user, discord.User):
            e.set_footer(text='This member is not in this server.')

        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def permissions(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
        """Shows a member's permissions in a specific channel.
        If no channel is given then it uses the current one.
        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = channel or ctx.channel
        if member is None:
            member = ctx.author

        await self.say_permissions(ctx, member, channel)

    @commands.command()
    @commands.guild_only()
    @default.mod_or_permissions(manage_roles=True)
    async def botpermissions(self, ctx, *, channel: discord.TextChannel = None):
        """Shows the bot's permissions in a specific channel.
        If no channel is given then it uses the current one.
        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.
        To execute this command you must have Manage Roles permission.
        You cannot use this in private messages.
        """
        channel = channel or ctx.channel
        member = ctx.guild.me
        await self.say_permissions(ctx, member, channel)

    @commands.command(aliases=['Dp'])
    @commands.is_owner()
    async def debugpermissions(self, ctx, guild_id: int, channel_id: int, author_id: int = None):
        """Shows permission resolution for a channel and an optional author."""

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await ctx.send('Guild not found?')

        channel = guild.get_channel(channel_id)
        if channel is None:
            return await ctx.send('Channel not found?')

        if author_id is None:
            member = guild.me
        else:
            member = await self.bot.get_or_fetch_member(guild, author_id)

        if member is None:
            return await ctx.send('Member not found?')

        await self.say_permissions(ctx, member, channel)

    @commands.command(aliases=['Se'])
    @commands.guild_only()
    @commands.has_permissions(manage_emojis=True)
    async def StealEmoji(self, ctx: commands.Context, emoji: discord.PartialEmoji, *roles: discord.Role):
        """This clones a specified emoji that optionally only specified roles
        are allowed to use.
        """
        # fetch the emoji asset and read it as bytes.
        # the key parameter here is `roles`, which controls
        # what roles are able to use the emoji.
        try:
            emoji_bytes = await emoji.read()
            await ctx.guild.create_custom_emoji(
                name=emoji.name,
                image=emoji_bytes,
                roles=roles,
                reason=f'Emoji yoinked by {ctx.author} VIA {ctx.guild.me.name}')
            send = f'{ctx.message.clean_content}'.replace(f'{ctx.prefix}{ctx.invoked_with}', '').replace(' ', '')
            await ctx.reply(
                embed=discord.Embed(description=f'{send} successfully stolen', color=random_color()).set_image(
                    url=emoji.url))
        except Exception as e:
            await ctx.send(str(e))


def setup(bot):
    bot.add_cog(Discord(bot))


class Embed(discord.Embed):
    pass
