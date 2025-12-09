import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='Jarvis', intents=intents)

@bot.event
async def on_ready():
    channel = bot.get_channel(1447202993119432747)
    await channel.send("Hello, I am J.A.R.V.I.S.")


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
    else:
        client = "sir"


    # call jarvis -> say command
    if message.content.lower() == "jarvis":
        await message.channel.send(f"Yes, {client}?")

        # Define a check so we only listen to *that same user* and *same channel*
        def check(m):
            return m.author == message.author and m.channel == message.channel
        try:
            # Wait for next message from the user
            reply = await bot.wait_for("message", check=check, timeout=30)

            if reply.content.lower() == "hi":
                await message.channel.send(f"Hello, {client}.")

            #if reply.content.lower() == "":


            else:
                await message.channel.send(f"I'm not sure what you mean, {client}.")
        except asyncio.TimeoutError:
            await message.channel.send(f"You took too long, {client}.")

    # let the bot process messages simultaneously
    await bot.process_commands(message)

bot.run(token)