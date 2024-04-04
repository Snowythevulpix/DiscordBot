import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import *
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

@bot.event
async def on_ready():
 print("ready")

@bot.slash_command(guild_ids=[1203822220250710046])
async def play(interaction:Interaction,search: str):
    query_string = urllib.parse.urlencode({'search_query': search})
    html_content = request.urlopen(
        'http://www.youtube.com/results?' + query_string)
    search_results = re.findall(
        'watch\?v=(.{11})', html_content.read().decode('utf-8'))
    url = ('https://www.youtube.com/watch?v=' + search_results[0])
    await interaction.send('https://www.youtube.com/watch?v=' + search_results[0])
    await join(interaction)
    await queue_(interaction, url)
    await p(interaction)

@bot.slash_command(guild_ids=[1203822220250710046])
async def queue_(interaction:Interaction, url):
    global queue
    queue.append(url)
    await interaction.send(f'`{url}` added to queue!')

@bot.slash_command(guild_ids=[1203822220250710046])
async def join(interaction:Interaction):
    channel = interaction.user.voice.channel
    voice = get(bot.voice_clients, guild=interaction.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await interaction.send("joining vc")

@bot.slash_command(guild_ids=[1203822220250710046])
async def leave(interaction:Interaction):
    channel = interaction.user.voice.channel
    voice = get(bot.voice_clients, guild=interaction.guild)
    if voice and voice.is_connected():
        voice = await channel.disconnect()
        await interaction.send("leaving vc")
    else:
        await interaction.send("you're not in a vc")

@bot.slash_command(guild_ids=[1203822220250710046])
async def p(interaction:Interaction):
    global queue
    print(queue)
    if not interaction.user.voice.channel:
        await interaction.send("This isnt the play command. please use ```/play``` insted")
        return
    elif len(queue) == 0:
        await interaction.send('This isnt the play command. please use ```/play``` insted')
    else:
        try:
            channel = interaction.message.author.voice.channel
            await channel.connect()
        except:
            pass

    server = interaction.guild
    voice_channel = server.voice_client
    while queue:
        try:
            while voice_channel.is_playing() or voice_channel.is_paused():
                await asyncio.sleep(2)
                pass
        except AttributeError:
            pass

        try:
            async with interaction.channel.typing():
                player = await YTDLSource.from_url(queue[0], loop=bot.loop)
                voice_channel.play(player, after=lambda e: print(
                    'Player error: %s' % e) if e else None)

                if loop:
                    queue.append(queue[0])
                del (queue[0])
            await interaction.send('**Now playing:** {}'.format(player.title))
        except:
            break



@bot.slash_command(guild_ids=[1203822220250710046])
async def pause(interaction:Interaction):
    voice = get(bot.voice_clients, guild=interaction.guild)
    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await interaction.send("Music Paused")
    else:
        print("Not playing, pause failed")
        await interaction.send("Pause Failed, not playing")

@bot.slash_command(guild_ids=[1203822220250710046])
async def resume(interaction:Interaction):
    voice = get(bot.voice_clients, guild=interaction.guild)
    if voice and voice.is_paused():
        print("Resuming Playback")
        voice.resume()
        await interaction.send("Resuming Playback")
    else:
        print("Not paused")
        await interaction.send("Not paused")

@bot.slash_command(guild_ids=[1203822220250710046])
async def stop(interaction:Interaction):
    voice = get(bot.voice_clients, guild=interaction.guild)
    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await interaction.send("Music stopped")
    else:
        print("Not playing")
        await interaction.send("Not playing")

@bot.slash_command(guild_ids=[1203822220250710046])
async def volume(interaction:Interaction, volume: int):
    if interaction.voice_client is None:
     return await interaction.send("Not connected to a voice channel.")

    interaction.voice_client.source.volume = volume / 100
    await interaction.send(f"Volume changed to {volume}%")

@bot.slash_command(guild_ids=[1203822220250710046])
async def skip(interaction:Interaction):
    voice = get(bot.voice_clients, guild=interaction.guild)
    if not voice.is_playing():
        raise NoMoreTracks
    voice.stop()
    await interaction.send("skipping song")



bot.run("YOUR TOKEN")