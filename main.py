import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='Jarvis', intents=intents)

@bot.event
async def on_ready():
    print("Yo")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.name == "your_zchy":
        await message.channel.send("shut up zboy")

    if message.author.name == "hrzckw":
        await message.channel.send("shut up mav")

    if message.content.lower() == "jarvis" and message.author.name == "chiaou":
        await message.channel.send("Yes, master?")
    elif message.content.lower() == "jarvis":
        await message.channel.send("Yes, sir?")

        # Define a check so we only listen to *that same user* and *same channel*
        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            # Wait for next message from the user
            reply = await client.wait_for("message", check=check, timeout=30)

            # Process the command
            if reply.content.lower() == "remove the last message":
                # delete the previous message (Jarvis's "Yes, sir?" or the user's "jarvis")
                async for msg in message.channel.history(limit=2):
                    await msg.delete()
                return

            else:
                await message.channel.send(f"Unknown command: {reply.content}")

        except asyncio.TimeoutError:
            await message.channel.send("You took too long, sir.")

    # let the bot process messages simultaneously
    await bot.process_commands(message)

bot.run(token)