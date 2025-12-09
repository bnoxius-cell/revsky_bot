import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import web
import yt_dlp

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    #channel = bot.get_channel(1447202993119432747)
    print("Hello, I am J.A.R.V.I.S.")


ytdlp_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True
}

@bot.command()
async def play(ctx, *, url):
    if ctx.author.voice is None:
        return await ctx.send("You need to be in a voice channel first.")

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    vc = ctx.voice_client

    if vc.is_playing():
        vc.stop()

    with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]

    source = discord.FFmpegPCMAudio(audio_url, executable=r"C:\Users\Ian\Documents\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe")
    vc.play(source)

    await ctx.send(f"Now playing: **{info.get('title')}**")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped and disconnected.")
    else:
        await ctx.send("I'm not in a voice channel.")




@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Clients
    client = ""
    if message.author.name == "chiaou":
        client = "Master Rin"
    elif message.author.name == "orekilvr":
        client = "Lady Jai"
    elif message.author.name == "meowjestickitty":
        client = "Cheska"
    else:
        client = "sir"


    # call jarvis -> say command
    if message.content.lower() == "jarvis":
        await message.channel.send(f"Yes, {client}?")
        # Define a check so we only listen to *that same user* and *same channel*
        def check(m):
            return m.author == message.author and m.channel == message.channel
        try:
            reply = await bot.wait_for("message", check=check, timeout=30)

            # COMMANDS:
            if reply.content.lower() == "hi":
                await message.channel.send(f"Hello, {client}.")

            if reply.content.lower() == "stroke it a lil" and client == "sir":
                await message.channel.send(f"For you, {client} — always.")


            if reply.content.lower() == "clean your messages":
                if not reply.author.guild_permissions.manage_messages:
                    await message.channel.send(f"Sorry, {client}. You can't do that.")
                    return

                async for msg in reply.channel.history(limit=10):
                    if msg.author == bot.user:
                        await msg.delete()
            if reply.content.lower() == "hey jude":
                await message.channel.send(f"this month's been bad.")

            # PURGE COMMAND
            if ("clear" in reply.content.lower() or "purge" in reply.content.lower()) and "message" in reply.content.lower():
                number = 0
                splittedText = reply.content.split()
                for i in splittedText:
                    if i.isdigit():
                        number = int(i) + 3
                async for msg in reply.channel.history(limit=number):
                    await msg.delete()
            else:
                await message.channel.send(f"I'm not sure what you mean, {client}.")
        except asyncio.TimeoutError:
            await message.channel.send(f"You took too long, {client}.")

    # let the bot process messages simultaneously
    await bot.process_commands(message)


bot.load_extension("cogs.music")
web.keep_alive()


bot.run(token)
