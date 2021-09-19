# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from collections import Counter
from io import BytesIO
from typing import Union
from unicodedata import name

import discord
from discord.ext import commands

from utils.checks import MemberConver
from utils.default import spacefill, date, CustomTimetext, config, mod_or_permissions
from utils.text_formatting import hyperlink, format_relative, format_date
from utils.vars import random_color, error, status


def diff(num1, num2):
    if num1 > num2:
        answer = num1 - num2
    elif num2 > num1:
        answer = num2 - num1
    else:
        answer = 0
    return answer

class MemberOrUser(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.MemberConverter().convert(ctx, argument)
        except commands.MemberNotFound:
            try:
                return await commands.UserConverter().convert(ctx, argument)
            except commands.UserNotFound:
                return None

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


class Discord(commands.Cog, description="Discord Information commands"):
    def __init__(self, bot):
        self.bot = bot
        self.config = config()

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour)
        avatar = member.display_avatar.with_static_format('png')
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
            nam = name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {nam} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg
                       )
    @commands.command(
        aliases=("av", "userpfp"), brief="Get member's avatar image"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx, user: MemberConver = None):
        jpg = user.avatar.with_format("jpg").url
        png = user.avatar.with_format("png").url
        webp = user.avatar.with_format("webp").url
        # Links to avatar (with different formats)
        links = (
            f"[JPG]({jpg})"
            f" | [PNG]({png})"
            f" | [WEBP]({webp})"
            )
        if user.avatar.is_animated():
            links += f" | [GIF]({user.avatar.with_format('gif').url})"

        # Embed stuff
        e = Embed(
            title=f"{user.name}'s Avatar",
            description=links,
        )
        e.set_image(url=user.avatar.with_size(1024).url)
        await ctx.try_reply(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1000, type=commands.BucketType.default)
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
                       file=discord.File(data, filename=f"{CustomTimetext('apache', 'Roles')}"))

    @commands.command(aliases=['JoinPos'])
    @commands.guild_only()
    async def joinedat(self, ctx, *, user: MemberConver = None):
        """ Check when a user joined the current server """
        user = user or ctx.author

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar.url)
        embed.description = f"**{user}** joined **{ctx.guild.name}**\n{date(user.joined_at, ago=True)}"
        await ctx.send(embed=embed)

    @commands.command(name="invite", aliases=["support", "inviteme", "botinvite"], brief="Sends an invite for the bot.")
    async def invite(self, ctx):
        """
        Sends an invite for the bot with no permissions.
        Note that a few permissions are required to let the bot run smoothly,
        as shown in `perms`
        """
        em = Embed(title=f"Invite {self.bot.user.name} to your server!")
        em.description = f'You like me huh? Invite me to your server with the link below. \n \
                          Run into any problems? Join the support server where we can help you out.\n\n\
                          Thank you for using me! \n\n \
                          {hyperlink("Dev`s links", "https://bio.link/edoC")} | \
                          {hyperlink("Source", "https://github.com/JakeWasChosen/edoC")}'

        class InviteView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(discord.ui.Button(label='Invite edoC!', url='https://discord.com/api/oauth2/authorize?client_id=845186772698923029&permissions=8&scope=bot%20applications.commands'))
                self.add_item(discord.ui.Button(label='Support Server', url='https://discord.gg/6EFAqm5aSG'))

        await ctx.send(embed=em, view=InviteView())

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

    @commands.command(aliases=['guildinfo', 'si', 'gi'])
    @commands.guild_only()
    async def serverinfo(self, ctx, *, guild_id: int = None):
        """Shows info about the current server."""
        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(
                    embed=discord.Embed(description='Invalid Guild ID given or im not in that guild', color=error))
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
        if ctx.guild.banner:
            e.set_image(url=ctx.guild.banner.with_format("png").with_size(1024))
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
        e.set_footer(text=f'Created {date(guild.created_at, ago=True)}')
        await ctx.send(embed=e)

    @commands.command(aliases=["aboutuser", "about_user", "userinfo", "user_info", "whoisme"])
    async def whois(self, ctx, *, user: Union[MemberConver, discord.User] = None):
        """Shows info about a user."""

        user = user or ctx.author
        e = discord.Embed(description='')
        roles = [role.name.replace('@', '@\u200b') for role in getattr(user, 'roles', []) if
                 not role.id == ctx.guild.default_role.id]
        bottag = '<:bot_tag:880193490556944435>'
        e.set_author(name=f'{user}{bottag if user.bot else ""}')
        join_position = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user) + 1

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

        e.description += f'Mobile {status(str(user.mobile_status))}  ' \
                         f'Desktop {status(str(user.desktop_status))}  ' \
                         f'Web browser {status(str(user.web_status))}'

        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def permissions(self, ctx, member: MemberConver = None, channel: discord.TextChannel = None):
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
    @mod_or_permissions(manage_roles=True)
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
    async def StealEmoji(self, ctx, emoji: discord.PartialEmoji, *roles: discord.Role):
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
