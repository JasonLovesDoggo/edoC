from discord import ClientException

import discord
import asyncio
import random
import youtube_dl
import string
import os
from discord.ext import commands
from googleapiclient.discovery import build
from discord.ext.commands import command
from utils import default, permissions
from utils.vars import *
from datetime import timedelta

ffmpegpath = "C:/Users/Jason/edoC/lib/ffmpeg/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg.exe"

# import pymongo
# NOTE: Import pymongo if you are using the database function commands
# NOTE: Also add `pymongo` and `dnspython` inside the requirements.txt file if you are using pymongo

# TODO: CREATE PLAYLIST SUPPORT FOR MUSIC


# NOTE: Without database, the music bot will not save your volume


# flat-playlist:True?
# extract_flat:True
# audioquality 0 best 9 worst
# format bestaudio/best or worstaudio
# 'noplaylist': None

ytdl_format_options = {
    'audioquality': 0,
    'format': 'bestaudio',
    'outtmpl': '{}',
    'restrictfilenames': True,
    'flatplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    "extractaudio": True,
    "audioformat": "opus",
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

# Download youtube-dl options
ytdl_download_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.mp3',
    'reactrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addreacses cause issues sometimes
    'source_addreacs': '0.0.0.0',
    'output': r'youtube-dl',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }]
}

stim = {
    'default_search': 'auto',
    "ignoreerrors": True,
    'quiet': True,
    "no_warnings": True,
    "simulate": True,  # do not keep the video files
    "nooverwrites": True,
    "keepvideo": False,
    "noplaylist": True,
    "skip_download": False,
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn',
    #'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}


class Downloader(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get("url")
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration')
        self.views = data.get('view_count')
        self.playlist = {}
        self.ffmpegpath = ffmpegpath

    @classmethod
    async def video_url(cls, url, ytdl, *, loop=None, stream=False):
        """
        Download the song file and data
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        song_list = {'queue': []}
        if 'entries' in data:
            if len(data['entries']) > 1:
                playlist_titles = [title['title'] for title in data['entries']]
                song_list = {'queue': playlist_titles}
                song_list['queue'].pop(0)

            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable=ffmpegpath, **ffmpeg_options,), data=data), song_list

    async def get_info(self, url):
        """
        Get the info of the next song by not downloading the actual file but just the data of song/query
        """
        yt = youtube_dl.YoutubeDL(stim)
        down = yt.extract_info(url, download=False)
        data1 = {'queue': []}
        if 'entries' in down:
            if len(down['entries']) > 1:
                playlist_titles = [title['title'] for title in down['entries']]
                data1 = {'title': down['title'], 'queue': playlist_titles}

            down = down['entries'][0]['title']

        return down, data1


class MusicPlayer(commands.Cog, name='Music'):
    def __init__(self, bot):
        self.config = default.config
        self.bot = bot
        self.checkmark = emojis["green_checkmark"]

        #self.music=self.database.find_one('music')
        self.player = {
            "audio_files": []
        }
        # self.database_setup()

    def database_setup(self):
        URL = os.getenv("MONGO")
        if URL is None:
            return False

    @property
    def random_color(self):
        return discord.Color.from_rgb(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))

    async def yt_info(self, song):
        """
        Get info from youtube
        """
        API_KEY = self.config["yt_google_api_key"]
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        song_data = youtube.search().list(part='snippet').execute()
        return song_data[0]

    @commands.Cog.listener('on_voice_state_update')
    async def music_voice(self, user, before, after):
        """
        Clear the server's playlist after bot leave the voice channel
        """
        if after.channel is None and user.id == self.bot.user.id:
            try:
                self.player[user.guild.id]['queue'].clear()
            except KeyError:
                # NOTE: server ID not in bot's local self.player dict
                # Server ID lost or was not in data before disconnecting
                print(f"Failed to get guild id {user.guild.id}")

    async def filename_generator(self):
        """
        Generate a unique file name for the song file to be named as
        """
        chars = list(string.ascii_letters + string.digits)
        name = 'C:/Users/Jason/edoC/lib/Music/Temp/'
        for i in range(random.randint(9, 25)):
            name += random.choice(chars)

        if name not in self.player['audio_files']:
            return name

        return await self.filename_generator()

    async def playlist(self, data, ctx):
        """
        THIS FUNCTION IS FOR WHEN YOUTUBE LINK IS A PLAYLIST
        Add song into the server's playlist inside the self.player dict
        """
        for i in data['queue']:
            print(i)
            self.player[ctx.guild.id]['queue'].append(
                {'title': i, 'author': ctx})

    async def queue(self, ctx, song):
        """
        Add the query/song to the queue of the server
        """
        title1 = await Downloader.get_info(self, url=song)
        title = title1[0]
        data = title1[1]
        # NOTE:needs fix here
        if data['queue']:
            await self.playlist(data, ctx)
            # NOTE: needs to be embeded to make it better output
            return await ctx.send(f"Added playlist {data['title']} to queue")
        self.player[ctx.guild.id]['queue'].append(
            {'title': title, 'author': ctx})
        #await ctx.reply(len(title.title()))
        return await ctx.send(f"**{title} added to queue**".title())

    async def voice_check(self, ctx):
        """
        function used to make bot leave voice channel if music not being played for longer than 2 minutes
        """
        if ctx.voice_client is not None:
            await asyncio.sleep(120)
            if ctx.voice_client is not None and ctx.voice_client.is_playing() is False and ctx.voice_client.is_paused() is False:
                await ctx.voice_client.disconnect()

    async def clear_data(self, ctx):
        """
        Clear the local dict data
            name - remove file name from dict
            remove file and filename from directory
            remove filename from global audio file names
        """
        name = self.player[ctx.guild.id]['name']
        os.remove(name)
        self.player['audio_files'].remove(name)

    async def loop_song(self, ctx):
        """
        Loop the currently playing song by replaying the same audio file via `discord.PCMVolumeTransformer()`
        """
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(self.player[ctx.guild.id]['name'], executable=ffmpegpath))
        loop = asyncio.get_event_loop()
        try:
            ctx.voice_client.play(
                source, after=lambda a: loop.create_task(self.done(ctx)))
            ctx.voice_client.source.volume = self.player[ctx.guild.id]['volume']
            # if str(ctx.guild.id) in self.music:
            #     ctx.voice_client.source.volume=self.music['vol']/100
        except Exception as Error:
            # Has no attribute play
            print(Error)  # NOTE: output back the error for later debugging

    async def done(self, ctx, ctxId: int = None):
        """
        Function to run once song completes
        Delete the "Now playing" message via ID
        """
        if ctxId:
            try:
                message = await ctx.channel.fetch_message(ctxId)
                await message.delete()
            except Exception as Error:
                print(f"Failed to get the message\n\n{Error}")

        if self.player[ctx.guild.id]['reset'] is True:
            self.player[ctx.guild.id]['reset'] = False
            return await self.loop_song(ctx)

        if ctx.guild.id in self.player and self.player[ctx.guild.id]['repeat'] is True:
            return await self.loop_song(ctx)

        await self.clear_data(ctx)

        if self.player[ctx.guild.id]['queue']:
            queue_data = self.player[ctx.guild.id]['queue'].pop(0)
            return await self.start_song(ctx=queue_data['author'], song=queue_data['title'])

        else:
            await self.voice_check(ctx)

    async def start_song(self, ctx, song):
        new_opts = ytdl_format_options.copy()
        audio_name = await self.filename_generator()

        self.player['audio_files'].append(audio_name)
        new_opts['outtmpl'] = new_opts['outtmpl'].format(audio_name)

        ytdl = youtube_dl.YoutubeDL(new_opts)
        download1 = await Downloader.video_url(song, ytdl=ytdl, loop=self.bot.loop)
        download = download1[0]
        data = download1[1]
        self.player[ctx.guild.id]['name'] = audio_name
        emb = discord.Embed(colour=self.random_color, title='Now Playing',
                            description=download.title, url=download.url)
        emb.set_thumbnail(url=download.thumbnail)
        views = "{:,}".format(download.views)
        emb.set_footer(text=f"{timedelta(seconds=download.duration)} views: {str(views)}\nRequested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        loop = asyncio.get_event_loop()

        if data['queue']:
            await self.playlist(data, ctx)

        ctxId = await ctx.send(embed=emb)
        self.player[ctx.guild.id]['player'] = download
        self.player[ctx.guild.id]['author'] = ctx
        try:
            ctx.voice_client.play(
                download, after=lambda a: loop.create_task(self.done(ctx, ctxId.id)))
        except ClientException:
            pass
        # if str(ctx.guild.id) in self.music: #NOTE adds user's default volume if in database
        #     ctx.voice_client.source.volume=self.music[str(ctx.guild.id)]['vol']/100
        ctx.voice_client.source.volume = self.player[ctx.guild.id]['volume']
        return ctx.voice_client

    @command()
    async def play(self, ctx, *, song):
        """
        Play a song with given url or title from Youtube
        `Ex:` s.play Titanium David Guetta
        `Command:` play(song_name)
        """
        if ctx.author.voice is None:
            return await ctx.send('**Please join a voice channel to play music**'.title())

        if ctx.guild.id in self.player:
            if ctx.voice_client.is_playing() is True:  # NOTE: SONG CURRENTLY PLAYING
                return await self.queue(ctx, song)

            if self.player[ctx.guild.id]['queue']:
                return await self.queue(ctx, song)

            if ctx.voice_client.is_playing() is False and not self.player[ctx.guild.id]['queue']:
                return await self.start_song(ctx, song)

        else:
            # IMPORTANT: THE ONLY PLACE WHERE NEW `self.player[ctx.guild.id]={}` IS CREATED
            self.player[ctx.guild.id] = {
                'player': None,
                'queue': [],
                'author': ctx,
                'name': None,
                "reset": False,
                'repeat': False,
                'volume': 0.5
            }
            return await self.start_song(ctx, song)

    @play.before_invoke
    async def before_play(self, ctx):
        """
        Check voice_client
            - User voice = None:
                please join a voice channel
            - bot voice == None:
                joins the user's voice channel
            - user and bot voice NOT SAME:
                - music NOT Playing AND queue EMPTY
                    join user's voice channel
                - items in queue:
                    please join the same voice channel as the bot to add song to queue
        """

        if ctx.voice_client is None:
            return await ctx.author.voice.channel.connect()

        if ctx.voice_client.channel != ctx.author.voice.channel:

            # NOTE: Check player and queue
            if ctx.voice_client.is_playing() is False and not self.player[ctx.guild.id]['queue']:
                return await ctx.voice_client.move_to(ctx.author.voice.channel)
                # NOTE: move bot to user's voice channel if queue does not exist

            if self.player[ctx.guild.id]['queue']:
                # NOTE: user must join same voice channel if queue exist
                return await ctx.send("Please join the same voice channel as the bot to add song to queue")

    @commands.has_permissions(manage_channels=True)
    @command(aliases=["playagain"])
    async def repeat(self, ctx):
        """
        Repeat the currently playing or turn off by using the command again
        `Ex:` ~repeat
        `Command:` repeat()
        """
        if ctx.guild.id in self.player:
            if ctx.voice_client.is_playing() is True:
                if self.player[ctx.guild.id]['repeat'] is True:
                    self.player[ctx.guild.id]['repeat'] = False
                    return await ctx.message.add_reaction(emoji=self.checkmark)

                self.player[ctx.guild.id]['repeat'] = True
                return await ctx.message.add_reaction(emoji=self.checkmark)

            return await ctx.send("No audio currently playing")
        return await ctx.send("Bot not in voice channel or playing music")

    @commands.has_permissions(manage_channels=True)
    @command(aliases=['restart-loop'])
    async def reset(self, ctx):
        """
        Restart the currently playing song  from the begining
        `Ex:` s.reset
        `Command:` reset()
        """
        if ctx.voice_client is None:
            return await ctx.send(f"**{ctx.author.display_name}, there is no audio currently playing from the bot.**")

        if ctx.author.voice is None or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send(f"**{ctx.author.display_name}, you must be in the same voice channel as the bot.**")

        if self.player[ctx.guild.id]['queue'] and ctx.voice_client.is_playing() is False:
            return await ctx.send("**No audio currently playing or songs in queue**".title(), delete_after=25)

        self.player[ctx.guild.id]['reset'] = True
        ctx.voice_client.stop()

    @commands.has_permissions(manage_channels=True)
    @command()
    async def skip(self, ctx):
        """
        Skip the current playing song
        `Ex:` s.skip
        `Command:` skip()
        """
        if ctx.voice_client is None:
            return await ctx.send("**No music currently playing**".title(), delete_after=60)

        if ctx.author.voice is None or ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send("Please join the same voice channel as the bot")

        if not self.player[ctx.guild.id]['queue'] and ctx.voice_client.is_playing() is False:
            return await ctx.send("**No songs in queue to skip**".title(), delete_after=60)

        self.player[ctx.guild.id]['repeat'] = False
        ctx.voice_client.stop()
        return await ctx.message.add_reaction(emoji=self.checkmark)

    @commands.has_permissions(manage_channels=True)
    @command()
    async def stop(self, ctx):
        """
        Stop the current playing songs and clear the queue
        `Ex:` s.stop
        `Command:` stop()
        """
        if ctx.voice_client is None:
            return await ctx.send("Bot is not connect to a voice channel")

        if ctx.author.voice is None:
            return await ctx.send("You must be in the same voice channel as the bot")

        if ctx.author.voice is not None and ctx.voice_client is not None:
            if ctx.voice_client.is_playing() is True or self.player[ctx.guild.id]['queue']:
                self.player[ctx.guild.id]['queue'].clear()
                self.player[ctx.guild.id]['repeat'] = False
                ctx.voice_client.stop()
                return await ctx.message.add_reaction(emoji=self.checkmark)

            return await ctx.send(
                f"**{ctx.author.display_name}, there is no audio currently playing or songs in queue**")

    @commands.has_permissions(manage_channels=True)
    @command(aliases=['get-out', 'disconnect', 'leave-voice'])
    async def leave(self, ctx):
        """
        Disconnect the bot from the voice channel
        `Ex:` s.leave
        `Command:` leave()
        """
        if ctx.author.voice is not None and ctx.voice_client is not None:
            if ctx.voice_client.is_playing() is True or self.player[ctx.guild.id]['queue']:
                self.player[ctx.guild.id]['queue'].clear()
                ctx.voice_client.stop()
                return await ctx.voice_client.disconnect(), await ctx.message.add_reaction(emoji=self.checkmark)

            return await ctx.voice_client.disconnect(), await ctx.message.add_reaction(emoji=self.checkmark)

        if ctx.author.voice is None:
            return await ctx.send("You must be in the same voice channel as bot to disconnect it via command")

    @commands.has_permissions(manage_channels=True)
    @command()
    async def pause(self, ctx):
        """
        Pause the currently playing audio
        `Ex:` s.pause
        `Command:` pause()
        """
        if ctx.author.voice is not None and ctx.voice_client is not None:
            if ctx.voice_client.is_paused() is True:
                return await ctx.send("Song is already paused")

            if ctx.voice_client.is_paused() is False:
                ctx.voice_client.pause()
                await ctx.message.add_reaction(emoji=self.checkmark)

    @commands.has_permissions(manage_channels=True)
    @command()
    async def resume(self, ctx):
        """
        Resume the currently paused audio
        `Ex:` s.resume
        `Command:` resume()
        """
        if ctx.author.voice is not None and ctx.voice_client is not None:
            if ctx.voice_client.is_paused() is False:
                return await ctx.send("Song is already playing")

            if ctx.voice_client.is_paused() is True:
                ctx.voice_client.resume()
                return await ctx.message.add_reaction(emoji=self.checkmark)

    @command(name='queue', aliases=['song-list', 'q', 'current-songs'])
    async def _queue(self, ctx):
        """
        Show the current songs in queue
        `Ex:` s.queue
        `Command:` queue()
        """
        if ctx.voice_client is not None:
            if ctx.guild.id in self.player:
                if self.player[ctx.guild.id]['queue']:
                    emb = discord.Embed(
                        colour=self.random_color, title='queue')
                    emb.set_footer(
                        text=f'Command used by {ctx.author.name}', icon_url=ctx.author.avatar_url)
                    for i in self.player[ctx.guild.id]['queue']:
                        emb.add_field(
                            name=f"**{i['author'].author.name}**", value=i['title'], inline=False)
                    return await ctx.send(embed=emb, delete_after=120)

        return await ctx.send("No songs in queue")

    @command(name='song-info', aliases=['song?', 'nowplaying', 'current-song'])
    async def song_info(self, ctx):
        """
        Show information about the current playing song
        `Ex:` s.song-info
        `Command:` song-into()
        """
        if ctx.voice_client is not None and ctx.voice_client.is_playing() is True:
            emb = discord.Embed(colour=self.random_color, title='Currently Playing',
                                description=self.player[ctx.guild.id]['player'].title)
            emb.set_footer(
                text=f"{self.player[ctx.guild.id]['author'].author.name}", icon_url=ctx.author.avatar_url)
            emb.set_thumbnail(
                url=self.player[ctx.guild.id]['player'].thumbnail)
            return await ctx.send(embed=emb, delete_after=120)

        return await ctx.send(f"**No songs currently playing**".title(), delete_after=30)

    @command(aliases=['move-bot', 'move-b', 'mb', 'mbot'])
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """
        Make bot join a voice channel you are in if no channel is mentioned
        `Ex:` .join (If voice channel name is entered, it'll join that one)
        `Command:` join(channel:optional)
        """
        if ctx.voice_client is not None:
            return await ctx.reply(f"Bot is already in a voice channel\nDid you mean to use {ctx.prefix}moveTo")

        if ctx.voice_client is None:
            if channel is None:
                return await ctx.author.voice.channel.connect(), await ctx.message.add_reaction(emoji=self.checkmark)

            return await channel.connect(), await ctx.message.add_reaction(emoji=self.checkmark)

        else:
            if ctx.voice_client.is_playing() is False and not self.player[ctx.guild.id]['queue']:
                return await ctx.author.voice.channel.connect(), await ctx.message.add_reaction(emoji=self.checkmark)

    @join.before_invoke
    async def before_join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel")

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return ctx.send(error)

        if error.args[0] == 'Command raised an exception: Exception: playing':
            return await ctx.send("**Please join the same voice channel as the bot to add song to queue**".title())

    @commands.has_permissions(manage_channels=True)
    @command(aliases=['vol'])
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
                    self.player[ctx.guild.id]['volume'] = vol
                    # if (ctx.guild.id) in self.music:
                    #     self.music[str(ctx.guild.id)]['vol']=vol
                    return await ctx.message.add_reaction(emoji=self.checkmark)

        return await ctx.send("**Please join the same voice channel as the bot to use the command**".title(),
                              delete_after=30)
    @commands.check(permissions.is_owner)
    @commands.command(brief='Download songs', description='~download <video url or title> Downloads the song')
    async def download(self, ctx, *, song):
        """
        Downloads the audio from given URL source and sends the audio source back to user to download from URL, the file will be removed from storage once sent.
        `Ex`: .download I'll Show you K/DA
        `Command`: download(url:required)
        `NOTE`: file size can't exceed 8MB, otherwise it will fail to upload and cause error
        """
        try:
            with youtube_dl.YoutubeDL(ytdl_download_format_options) as ydl:
                if "https://www.youtube.com/" in song:
                    download = ydl.extract_info(song, True)
                else:
                    infosearched = ydl.extract_info(
                        "ytsearch:" + song, False)
                    download = ydl.extract_info(
                        infosearched['entries'][0]['webpage_url'], True)
                filename = ydl.prepare_filename(download)
                embed = discord.Embed(
                    title="Your download is ready",
                    description="Please wait a moment while the file is beeing uploaded")
                await ctx.send(embed=embed, delete_after=30)
                await ctx.send(file=discord.File(filename))
                os.remove(filename)
        except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError):
            embed = discord.Embed(title="Song couldn't be downloaded", description=("Song:" + song))
            await ctx.send(embed=embed)

    @volume.error
    async def volume_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send("Manage channels or admin perms required to change volume", delete_after=30)


def setup(bot):
    bot.add_cog(MusicPlayer(bot))
