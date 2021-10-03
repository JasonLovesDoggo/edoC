# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import datetime
import io
import os
import re
import zlib

import discord
import lxml.etree as etree
from discord.ext import commands

from .utils import fuzzy, time

DISCORD_API_ID    = 81384788765712384
DISCORD_BOTS_ID   = 110373943822540800
USER_BOTS_ROLE    = 178558252869484544
CONTRIBUTORS_ROLE = 111173097888993280
DISCORD_PY_ID     = 84319995256905728
DISCORD_PY_GUILD  = 336642139381301249
DISCORD_PY_PROF_ROLE = 381978395270971407
DISCORD_PY_HELPER_ROLE = 558559632637952010
DISCORD_PY_HELP_CHANNELS = (381965515721146390, 564950631455129636, 738572311107469354)
BOT_LIST_INFO = {
    DISCORD_API_ID: {
        'channel':580184108794380298,
        'testing': (
            381896832399310868, #testing
            381896931724492800, #playground
        ),
        'terms': 'By requesting to add your bot, you agree to not spam or do things without user input.'
    },
    DISCORD_PY_GUILD: {
        'channel': 579998326557114368,
        'testing': (
            381963689470984203, #testing
            559455534965850142, #playground
            568662293190148106, #mod-testing
        ),
        'terms': 'By requesting to add your bot, you must agree to the guidelines presented in the <#381974649019432981>.'
    }
}

#def in_testing(info=BOT_LIST_INFO):
#    def predicate(ctx):
#        try:
#            return ctx.channel.id in info[ctx.guild.id]['testing']
#        except (AttributeError, KeyError):
#            return False
#    return commands.check(predicate)

#def is_discord_py_helper(member):
#    guild_id = member.guild.id
#    if guild_id != DISCORD_PY_GUILD:
#        return False
#
#    if member.guild_permissions.manage_roles:
#        return False
#
#    return member._roles.has(DISCORD_PY_HELPER_ROLE)
#
#def can_use_block():
#    def predicate(ctx):
#        if ctx.guild is None:
#            return False
#
#        guild_id = ctx.guild.id
#        if guild_id == DISCORD_API_ID:
#            return ctx.channel.permissions_for(ctx.author).manage_roles
#        elif guild_id == DISCORD_PY_GUILD:
#            guild_level = ctx.author.guild_permissions
#            return guild_level.manage_roles
#        return False
#    return commands.check(predicate)
#
#def can_use_tempblock():
#    def predicate(ctx):
#        if ctx.guild is None:
#            return False
#
#        guild_id = ctx.guild.id
#        if guild_id == DISCORD_API_ID:
#            return ctx.channel.permissions_for(ctx.author).manage_roles
#        elif guild_id == DISCORD_PY_GUILD:
#            guild_level = ctx.author.guild_permissions
#            return guild_level.manage_roles or (
#                ctx.channel.id in DISCORD_PY_HELP_CHANNELS and
#                (ctx.author._roles.has(DISCORD_PY_PROF_ROLE) or
#                 ctx.author._roles.has(DISCORD_PY_HELPER_ROLE))
#            )
#        return False
#    return commands.check(predicate)
#
#def contributor_or_higher():
#    def predicate(ctx):
#        guild = ctx.guild
#        if guild is None:
#            return False
#
#        role = discord.utils.find(lambda r: r.id == CONTRIBUTORS_ROLE, guild.roles)
#        if role is None:
#            return False
#
#        return ctx.author.top_role >= role
#    return commands.check(predicate)



class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')

class API(commands.Cog):
    """Discord API exclusive things."""

    def __init__(self, bot):
        self.bot = bot
        self.issue = re.compile(r'##(?P<number>[0-9]+)')
        self._recently_blocked = set()

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{PERSONAL COMPUTER}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != DISCORD_API_ID:
            return

        if member.bot:
            role = discord.Object(id=USER_BOTS_ROLE)
            await member.add_roles(role)

    def parse_object_inv(self, stream, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            sub = cache[key] = {}
            async with self.bot.session.get(page + '/objects.inv') as resp:
                if resp.status != 200:
                    raise RuntimeError('Cannot build rtfm lookup table, try again later.')

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(self, ctx, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'latest-jp': 'https://discordpy.readthedocs.io/ja/latest',
            'python': 'https://docs.python.org/3',
            'python-jp': 'https://docs.python.org/ja/3',
            'master': 'https://discordpy.readthedocs.io/en/master',
        }

        if obj is None:
            await ctx.send(page_types[key])
            return

        if not hasattr(self, '_rtfm_cache'):
            await ctx.trigger_typing()
            await self.build_rtfm_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            # point the abc.Messageable types properly:
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())
        def transform(tup):
            return tup[0]

        matches = fuzzy.finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        e = discord.Embed(colour=discord.Colour.blurple())
        if len(matches) == 0:
            return await ctx.send('Could not find anything. Sorry.')

        e.description = '\n'.join(f'[`{key}`]({url})' for key, url in matches)
        await ctx.send(embed=e, reference=ctx.replied_reference)

        if ctx.guild and ctx.guild.id in (DISCORD_API_ID, DISCORD_PY_GUILD):
            query = 'INSERT INTO rtfm (user_id) VALUES ($1) ON CONFLICT (user_id) DO UPDATE SET count = rtfm.count + 1;'
            await ctx.db.execute(query, ctx.author.id)

    def transform_rtfm_language_key(self, ctx, prefix):
        if ctx.guild is not None:
            #                             ??? category
            if ctx.channel.category_id == 490287576670928914:
                return prefix + '-jp'
            #                    d.py unofficial JP   Discord Bot Portal JP
            elif ctx.guild.id in (463986890190749698, 494911447420108820):
                return prefix + '-jp'
        return prefix

    @commands.group(aliases=['rtfd'], invoke_without_command=True)
    async def rtfm(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity.
        Events, objects, and functions are all supported through
        a cruddy fuzzy algorithm.
        """
        key = self.transform_rtfm_language_key(ctx, 'latest')
        await self.do_rtfm(ctx, key, obj)

    @rtfm.command(name='jp')
    async def rtfm_jp(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity (Japanese)."""
        await self.do_rtfm(ctx, 'latest-jp', obj)

    @rtfm.command(name='python', aliases=['py'])
    async def rtfm_python(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a Python entity."""
        key = self.transform_rtfm_language_key(ctx, 'python')
        await self.do_rtfm(ctx, key, obj)

    @rtfm.command(name='py-jp', aliases=['py-ja'])
    async def rtfm_python_jp(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a Python entity (Japanese)."""
        await self.do_rtfm(ctx, 'python-jp', obj)

    @rtfm.command(name='master', aliases=['2.0'])
    async def rtfm_master(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity (master branch)"""
        await self.do_rtfm(ctx, 'master', obj)

    async def _member_stats(self, ctx, member, total_uses):
        e = discord.Embed(title='RTFM Stats')
        e.set_author(name=str(member), icon_url=member.display_avatar.url)

        query = 'SELECT count FROM rtfm WHERE user_id=$1;'
        record = await ctx.db.fetchrow(query, member.id)

        if record is None:
            count = 0
        else:
            count = record['count']

        e.add_field(name='Uses', value=count)
        e.add_field(name='Percentage', value=f'{count/total_uses:.2%} out of {total_uses}')
        e.colour = discord.Colour.blurple()
        await ctx.send(embed=e)

    @rtfm.command()
    async def stats(self, ctx, *, member: discord.Member = None):
        """Tells you stats about the ?rtfm command."""
        query = 'SELECT SUM(count) AS total_uses FROM rtfm;'
        record = await ctx.db.fetchrow(query)
        total_uses = record['total_uses']

        if member is not None:
            return await self._member_stats(ctx, member, total_uses)

        query = 'SELECT user_id, count FROM rtfm ORDER BY count DESC LIMIT 10;'
        records = await ctx.db.fetch(query)

        output = []
        output.append(f'**Total uses**: {total_uses}')

        # first we get the most used users
        if records:
            output.append(f'**Top {len(records)} users**:')

            for rank, (user_id, count) in enumerate(records, 1):
                user = self.bot.get_user(user_id) or (await self.bot.fetch_user(user_id))
                if rank != 10:
                    output.append(f'{rank}\u20e3 {user}: {count}')
                else:
                    output.append(f'\N{KEYCAP TEN} {user}: {count}')

        await ctx.send('\n'.join(output))

    def library_name(self, channel):
        # language_<name>
        name = channel.name
        index = name.find('_')
        if index != -1:
            name = name[index + 1:]
        return name.replace('-', '.')

    def get_block_channels(self, guild, channel):
        if guild.id == DISCORD_PY_GUILD and channel.id in DISCORD_PY_HELP_CHANNELS:
            return [guild.get_channel(x) for x in DISCORD_PY_HELP_CHANNELS]
        return [channel]

    @commands.command()
    @can_use_block()
    async def block(self, ctx, *, member: discord.Member):
        """Blocks a user from your channel."""

        if member.top_role >= ctx.author.top_role:
            return

        reason = f'Block by {ctx.author} (ID: {ctx.author.id})'

        channels = self.get_block_channels(ctx.guild, ctx.channel)

        try:
            for channel in channels:
                await channel.set_permissions(member, send_messages=False, add_reactions=False, reason=reason)
        except:
            await ctx.send('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.send('\N{THUMBS UP SIGN}')

    @commands.command()
    @can_use_block()
    async def unblock(self, ctx, *, member: discord.Member):
        """Unblocks a user from your channel."""

        if member.top_role >= ctx.author.top_role:
            return

        reason = f'Unblock by {ctx.author} (ID: {ctx.author.id})'

        channels = self.get_block_channels(ctx.guild, ctx.channel)

        try:
            for channel in channels:
                await channel.set_permissions(member, send_messages=None, add_reactions=None, reason=reason)
        except:
            await ctx.send('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.send('\N{THUMBS UP SIGN}')


    @commands.command()
    @can_use_tempblock()
    async def tempblock(self, ctx, duration: time.FutureTime, *, member: discord.Member):
        """Temporarily blocks a user from your channel.
        The duration can be a a short time form, e.g. 30d or a more human
        duration such as "until thursday at 3PM" or a more concrete time
        such as "2017-12-31".
        Note that times are in UTC.
        """

        if member.top_role >= ctx.author.top_role:
            return

        created_at = ctx.message.created_at
        if is_discord_py_helper(ctx.author) and duration.dt > (created_at + datetime.timedelta(minutes=60)):
            return await ctx.send('Helpers can only block for up to an hour.')

        reminder = self.bot.get_cog('Reminder')
        if reminder is None:
            return await ctx.send('Sorry, this functionality is currently unavailable. Try again later?')

        channels = self.get_block_channels(ctx.guild, ctx.channel)
        timer = await reminder.create_timer(duration.dt, 'tempblock', ctx.guild.id, ctx.author.id,
                                                                      ctx.channel.id, member.id,
                                                                      connection=ctx.db,
                                                                      created=created_at)

        reason = f'Tempblock by {ctx.author} (ID: {ctx.author.id}) until {duration.dt}'

        try:
            for channel in channels:
                await channel.set_permissions(member, send_messages=False, add_reactions=False, reason=reason)
        except:
            await ctx.send('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.send(f'Blocked {member} for {time.format_relative(duration.dt)}.')

    @commands.Cog.listener()
    async def on_tempblock_timer_complete(self, timer):
        guild_id, mod_id, channel_id, member_id = timer.args

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            # RIP
            return

        channel = guild.get_channel(channel_id)
        if channel is None:
            # RIP x2
            return

        to_unblock = await self.bot.get_or_fetch_member(guild, member_id)
        if to_unblock is None:
            # RIP x3
            return

        moderator = await self.bot.get_or_fetch_member(guild, mod_id)
        if moderator is None:
            try:
                moderator = await self.bot.fetch_user(mod_id)
            except:
                # request failed somehow
                moderator = f'Mod ID {mod_id}'
            else:
                moderator = f'{moderator} (ID: {mod_id})'
        else:
            moderator = f'{moderator} (ID: {mod_id})'


        reason = f'Automatic unblock from timer made on {timer.created_at} by {moderator}.'

        for ch in self.get_block_channels(guild, channel):
            try:
                await ch.set_permissions(to_unblock, send_messages=None, add_reactions=None, reason=reason)
            except:
                pass

    async def refresh_faq_cache(self):
        self.faq_entries = {}
        base_url = 'https://discordpy.readthedocs.io/en/latest/faq.html'
        async with self.bot.session.get(base_url) as resp:
            text = await resp.text(encoding='utf-8')

            root = etree.fromstring(text, etree.HTMLParser())
            nodes = root.findall(".//div[@id='questions']/ul[@class='simple']/li/ul//a")
            for node in nodes:
                self.faq_entries[''.join(node.itertext()).strip()] = base_url + node.get('href').strip()

    @commands.command()
    async def faq(self, ctx, *, query: str = None):
        """Shows an FAQ entry from the discord.py documentation"""
        if not hasattr(self, 'faq_entries'):
            await self.refresh_faq_cache()

        if query is None:
            return await ctx.send('https://discordpy.readthedocs.io/en/latest/faq.html')

        matches = fuzzy.extract_matches(query, self.faq_entries, scorer=fuzzy.partial_ratio, score_cutoff=40)
        if len(matches) == 0:
            return await ctx.send('Nothing found...')

        paginator = commands.Paginator(suffix='', prefix='')
        for key, _, value in matches:
            paginator.add_line(f'**{key}**\n{value}')
        page = paginator.pages[0]
        await ctx.send(page, reference=ctx.replied_reference)


def setup(bot):
    bot.add_cog(API(bot))