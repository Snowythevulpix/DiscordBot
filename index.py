import asyncio
import nextcord
from nextcord.ext import commands
import yt_dlp as youtube_dl
from nextcord.utils import get
import datetime
import re
from urllib import request
import urllib.parse
import os

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class NoMoreTracks(Exception):
    pass

queue = []
loop = False

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.9):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command()
async def p(ctx, *, search):
    query_string = urllib.parse.urlencode({'search_query': search})
    html_content = request.urlopen(
        'http://www.youtube.com/results?' + query_string)
    search_results = re.findall(
        'watch\?v=(.{11})', html_content.read().decode('utf-8'))
    url = ('https://www.youtube.com/watch?v=' + search_results[0])
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])
    await join(ctx)
    await queue_(ctx, url)
    await play(ctx)

@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

@bot.command(pass_context=True)
async def play(ctx):
    global queue
    print(queue)
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    elif len(queue) == 0:
        await ctx.send('Nothing in your queue! Use `!p` to add a song!')
    else:
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        except:
            pass

    server = ctx.message.guild
    voice_channel = server.voice_client
    while queue:
        try:
            while voice_channel.is_playing() or voice_channel.is_paused():
                await asyncio.sleep(2)
                pass
        except AttributeError:
            pass

        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(queue[0], loop=bot.loop)
                voice_channel.play(player, after=lambda e: print(
                    'Player error: %s' % e) if e else None)

                if loop:
                    queue.append(queue[0])
                del (queue[0])
            await ctx.send('**Now playing:** {}'.format(player.title))
        except:
            break

@bot.command()
async def queue_(ctx, url):
    global queue
    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')

@bot.command(pass_context=True)
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music Paused")
    else:
        print("Not playing, pause failed")
        await ctx.send("Pause Failed, not playing")

@bot.command(pass_context=True)
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        print("Resuming Playback")
        voice.resume()
        await ctx.send("Resuming Playback")
    else:
        print("Not paused")
        await ctx.send("Not paused")

@bot.command(pass_context=True)
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("Not playing")
        await ctx.send("Not playing")

@bot.command()
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send("Not connected to a voice channel.")

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Volume changed to {volume}%")

@bot.command()
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice.is_playing():
        raise NoMoreTracks
    voice.stop()
    await ctx.send("Next song")

bot.run("your bot's token")