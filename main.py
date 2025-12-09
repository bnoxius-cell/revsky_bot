import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import web

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

web.keep_alive()
bot.run(token)
