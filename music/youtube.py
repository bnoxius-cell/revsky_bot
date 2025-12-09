import yt_dlp
import discord
from discord.ext import commands
import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def play(ctx, url):
    voice = ctx.author.voice.channel

    if ctx.voice_client is None:
        await voice.connect()

    vc = ctx.voice_client

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
    FFMPEG_OPTIONS = {'options': '-vn'}

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))

    await ctx.send(f"🎶 Now playing: {info['title']}")


@bot.command()
async def join(ctx):
    voice = ctx.author.voice.channel

    if ctx.voice_client is None:
        await voice.connect()

    vc = ctx.voice_client