# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from datetime import datetime

import DiscordUtils
import discord
import humanfriendly
from discord.ext import commands, tasks
from discord.ext.commands import is_owner

from utils.checks import UrlSafe
from utils.default import is_dj_or_perms, is_admin
from utils.pagination import Paginator
from utils.vars import *

music_ = DiscordUtils.Music()


# i wrote this cog while sleeping
# dont ask
def success_embed(title, description):
    return discord.Embed(
        title=title,
        description=description,
        color=blue
    )


class music(commands.Cog, description="Jam to some awesome tunes! ?"):
    def __init__(self, bot):
        self.bot = bot
        self.check = '<a:checkmark:878104445702008842>'
        self.off = 'https://i.imgur.com/fNksG3T.png'
        self.on = 'https://i.imgur.com/xZGE55G.png'
        self.onemoji = '<:on:878405331766624267>'
        self.offemoji = '<:off:878405303866118214>'
        self.skip_votes = {}
        #self.my_background_task.start()

    def error_msg(self, error):
        if error == 'not_in_voice_channel':
            return f"{emojis['red_x']}You need to join a voice channel first."
        elif error == 'not_in_same_vc':
            return f"{emojis['red_x']}You need to be in the same voice channel as me."
        else:
            return "An error occurred ._."

    async def leavechnl(self, ctx):
        player = music_.get_player(guild_id=ctx.guild.id)
        if player:
            try:
                await player.stop()
                await player.delete()
            except Exception:
                pass
        await ctx.voice_client.disconnect()
        await ctx.message.add_reaction(self.check)

    def now_playing_embed(self, ctx, song):
        return discord.Embed(
            title=song.title,
            url=song.url,
            color=blue,
            timestamp=datetime.utcnow(),
            description=f"""
**Duration:** {humanfriendly.format_timespan(song.duration)}
**Channel:** [{song.channel}]({song.channel_url})
                        """
        ).set_image(url=song.thumbnail
                    ).set_footer(text=f"Loop: {'on' if song.is_looping else 'off'}",
                                 icon_url=f'{self.on if song.is_looping else self.off}'
                                 ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

    @tasks.loop(minutes=30)  # task runs every 30 minutes
    async def my_background_task(self):
        channel = self.bot.get_channel(865315406130446366)  # channel ID goes here
        await channel.send(str(1 + 124234))

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()  # wait until the bot logs in

    @commands.command(help="I will join your voice channel.", aliases=['connect'])
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def join(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if ctx.guild.me.voice and len(ctx.guild.me.voice.channel.members) > 1:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("Someone else is already using the bot :c")
        try:
            await ctx.author.voice.channel.connect()
            await ctx.message.add_reaction(self.check)
        except Exception:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(
                "I wasn't able to connect to your voice channel.\nPlease make sure I have enough permissions.")

    @commands.command(aliases=['vol'])
    @is_dj_or_perms()
    async def volume(self, ctx, vol: int):
        """
        Change the volume of the bot
        `Ex:` .vol 100 (200 is the max)
        `Permission:` manage_channels
        `Command:` volume(amount:integer)
        """

        if vol > 200:
            vol = 200
        vol = vol / 100
        if ctx.author.voice is not None:
            if ctx.voice_client is not None:
                if ctx.voice_client.channel == ctx.author.voice.channel and ctx.voice_client.is_playing() is True:
                    ctx.voice_client.source.volume = vol
                    return await ctx.message.add_reaction(self.check)
        return await ctx.send("**Please join the same voice channel as the bot to use the command**".title(),
                              delete_after=30)

    @commands.command(help="I will leave your voice channel :c", aliases=['dc', 'disconnect'])
    @commands.cooldown(3, 5, commands.BucketType.user)
    @is_dj_or_perms()
    async def leave(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        elif not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not in a voice channel ._.")
        elif ctx.author.voice.channel != ctx.guild.me.voice.channel:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg("not_in_same_vc"))
        elif ctx.author.voice.channel == ctx.guild.me.voice.channel:
            if len(ctx.guild.me.voice.channel.members) == 2:
                await self.leavechnl(ctx)
            elif ctx.author.guild_permissions.manage_channels:
                await self.leavechnl(ctx)
            else:
                return await ctx.reply(embed=discord.Embed(
                    description=f'You need to either be alone with the bot or have manage channel permissions',
                    color=error))

    @commands.command(help="I will leave the voice channel :c bypassing checks",
                      aliases=['fdc', 'forcedisconnect'],
                      brief='Leave the vc bypassing checks')
    @commands.check_any(is_admin(), is_owner())
    async def ForceLeave(self, ctx):
        if not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not in a voice channel ._.")
        await self.leavechnl(ctx)

    @commands.command(help="V I B E and play epik music!!!", aliases=['p'])
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def play(self, ctx, *, song_=None):
        if song_ is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(
                f"Correct Usage: `{ctx.clean_prefix}play <song/url>`\nExample: `{ctx.clean_prefix}play Rick Roll`")
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if not ctx.guild.me.voice:
            await ctx.invoke(self.bot.get_command('join'))
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            player = music_.create_player(ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            try:
                await player.queue(song_, search=True, bettersearch=True)
            except Exception:
                await player.queue(song_, search=True)
            song = await player.play()
            await ctx.send(embed=self.now_playing_embed(ctx, song))
        else:
            try:
                song = await player.queue(song_, search=True, bettersearch=True)
            except Exception:
                song = await player.queue(song_, search=True)
            await ctx.send(embed=discord.Embed(
                title=song.title,
                url=song.url,
                color=blue,
                description=f"""
**Duration:** {humanfriendly.format_timespan(song.duration)}
**Channel:** [{song.channel}]({song.channel_url})
                            """
            ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url
                         ).set_thumbnail(url=song.thumbnail
                                         ).set_footer(
                text=f"Song added to queue | Loop: {'on' if song.is_looping else 'off'}",
                icon_url=f'{self.on if song.is_looping else self.off}'))

    @commands.command(help="Check the current playing song.", aliases=['np'])
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def nowplaying(self, ctx):
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            return await ctx.reply("Nothing is playing rn.")
        if not ctx.voice_client.is_playing():
            return await ctx.reply("No music playing rn ._.")
        song = player.now_playing()
        await ctx.reply(embed=self.now_playing_embed(ctx, song))

    @commands.command(help="Pause the song.")
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def pause(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not playing any songs ._.")
        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg("not_in_same_vc"))
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not playing any songs ._.")
        try:
            await player.pause()
        except DiscordUtils.NotPlaying:
            return await ctx.reply("I am not playing any songs ._.")
        await ctx.message.add_reaction(self.check)

    @commands.command(help="Resume the song.")
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def resume(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not in a voice channel ._.")
        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg("not_in_same_vc"))
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not playing any songs ._.")
        try:
            await player.resume()
        except DiscordUtils.NotPlaying:
            return await ctx.reply("I am not playing any songs ._.")
        await ctx.message.add_reaction(self.check)

    @commands.command(help="Stop the player.")
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def stop(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not in a voice channel ._.")
        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg("not_in_same_vc"))
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not playing any songs ._.")
        try:
            await player.stop()
        except DiscordUtils.NotPlaying:
            return await ctx.reply("I am not playing any songs ._.")
        await ctx.message.add_reaction(self.check)

    @commands.command(help="Toggle song loop!")
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def loop(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not in a voice channel ._.")
        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg("not_in_same_vc"))
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("There is no music playing, please queue some songs.")
        try:
            song = await player.toggle_song_loop()
        except DiscordUtils.NotPlaying:
            return await ctx.reply("I am not playing any songs ._.")
        if song.is_looping:
            await ctx.reply(embed=discord.Embed(description=f"{self.onemoji} Looping `{song.name}`", color=green))
        else:
            await ctx.reply(embed=discord.Embed(description=f"{self.offemoji} Loop disabled.", color=error))

    @commands.command(help="Check the song queue!", aliases=['q', 'que'])
    async def queue(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not in a voice channel ._.")
        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg("not_in_same_vc"))
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("There is no music playing, please queue some songs.")
        try:
            queue_ = player.current_queue()
        except DiscordUtils.EmptyQueue:
            return await ctx.reply("The queue is empty ._.")

        nice = ""
        i = 1
        for song_ in queue_:  # i will paginate this later when i feel like not being lazy
            if i == 11:
                break
            nice += f"`{i}.{' ' if i != 10 else ''}` ~ [{song_.title}]({song_.url})\n"
            i += 1

        return await ctx.reply(embed=success_embed(
            ":notes: Queue!",
            nice
        ))

    @commands.command()
    @is_dj_or_perms()
    async def remove(self, ctx, index):
        player = music_.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index))
        await ctx.send(f"Removed {song.name} from queue")

    @commands.command(help="Skip a song.", aliases=['voteskip'])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def skip(self, ctx):
        if not ctx.author.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg('not_in_voice_channel'))
        if not ctx.guild.me.voice:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("I am not in a voice channel ._.")
        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            ctx.command.reset_cooldown(ctx)
            return await ctx.error(self.error_msg("not_in_same_vc"))
        player = music_.get_player(guild_id=ctx.guild.id)
        if not player:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("There is no music playing, please queue some songs.")
        if not ctx.voice_client.is_playing():
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("There is no music playing ._.")

        hoomans = len(list(filter(lambda m: not m.bot, ctx.author.voice.channel.members)))
        if hoomans <= 2 or ctx.author.guild_permissions.manage_guild:
            try:
                await player.skip(force=True)
                await ctx.message.add_reaction(self.check)
                if ctx.guild.id in self.skip_votes:
                    self.skip_votes.pop(ctx.guild.id)
                return
            except DiscordUtils.NotPlaying:
                return await ctx.reply("There is no music playing ._.")

        if ctx.guild.id not in self.skip_votes:
            self.skip_votes.update({ctx.guild.id: [ctx.author.id]})
            await ctx.reply(f"?? Vote skipping has been started: `1/{round(hoomans / 2)}` votes.")
        else:
            old_list = self.skip_votes[ctx.guild.id]
            if ctx.author.id in old_list:
                return await ctx.reply("You have already added your skip vote!")
            old_list.append(ctx.author.id)
            self.skip_votes.update({ctx.guild.id: old_list})
            if len(self.skip_votes[ctx.guild.id]) >= round(hoomans / 2):
                try:
                    await player.skip(force=True)
                    self.skip_votes.pop(ctx.guild.id)
                    await ctx.message.add_reaction(self.check)
                except DiscordUtils.NotPlaying:
                    return await ctx.reply("There is no music playing ._.")
            else:
                await ctx.reply(
                    f"?? Skip vote added: `{len(self.skip_votes[ctx.guild.id])}/{round(hoomans / 2)}` votes.")

    @commands.command(help="Get lyrics of a song. Example: `~lyrics Never Gonna Give You Up`", brief='Get lyrics of a song.', aliases=['lyrc', 'lyric'])
    async def lyrics(self, ctx, *, song: UrlSafe = None):
        error_msg = f"Please enter the song name.\nExample: `{ctx.clean_prefix}lyrics Never Gonna Give You Up`"
        if song is None:
            player = music_.get_player(guild_id=ctx.guild.id)
            if not player:
                return await ctx.reply(error_msg)
            if not ctx.voice_client.is_playing():
                return await ctx.reply(error_msg)
            current_song = player.now_playing()
            song = current_song.name
        embeds = []
        async with self.bot.session.get(
                f'https://some-random-api.ml/lyrics?title={song.title()}') as r:
            rj = await r.json()
            errr = rj.get('error')
            if errr:
                return await ctx.error(f'Recieved unexpected error: {errr}')
            if len(rj['lyrics']) <= 4000:
                return await ctx.reply(embed=discord.Embed(
                    title=rj['title'],
                    url=rj['links']['genius'],
                    description=rj['lyrics'],
                    color=invis
                ).set_thumbnail(url=rj['thumbnail']['genius']))
            i = 0
            while True:
                if len(rj['lyrics']) - i > 4000:
                    embeds.append(discord.Embed(
                        title=rj['title'],
                        url=rj['links']['genius'],
                        description=rj['lyrics'][i:i + 3999],
                        color=invis
                    ).set_thumbnail(url=rj['thumbnail']['genius']))
                elif len(rj['lyrics']) - i <= 0:
                    break
                else:
                    embeds.append(discord.Embed(
                        title=rj['title'],
                        url=rj['links']['genius'],
                        description=rj['lyrics'][i:len(rj['lyrics']) - 1],
                        color=invis
                    ).set_thumbnail(url=rj['thumbnail']['genius']))
                    break
                i += 3999
            return await ctx.reply(embed=embeds[0], view=Paginator(ctx=ctx, embeds=embeds))


def setup(bot):
    bot.add_cog(music(bot))
