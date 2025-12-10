import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import web
from openai import OpenAI
import yt_dlp

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=discord.Intents.all())
ai = OpenAI(api_key=OPENAI_API_KEY)

bot = commands.Bot(command_prefix='$', intents=intents)



def load_jarvis_persona(filepath="jarvis_persona.txt"):
    with open(filepath, 'r', encoding='utf-8') as file:
        persona_text = file.read()
    return persona_text

async def generate_reply(message, targets):
    response = ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": load_jarvis_persona()},
            {"role": "user", "content": message, "pronoun": targets}
        ]
    )
    return response.choices[0].message.content


@bot.event
async def on_ready():
    #channel = bot.get_channel(1447202993119432747)
    print("Hello, I am J.A.R.V.I.S.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Clients
    target_user = ""
    if message.author.name == "chiaou":
        target_user = "Master Rin"
    elif message.author.name == "orekilvr":
        target_user = "Lady Jai"
    elif message.author.name == "meowjestickitty":
        target_user = "Cheska"
    elif message.author.name == "chitandalvr":
        target_user = "Creator"
    else:
        target_user = "sir"


    # call jarvis -> say command
    if "jarvis" in message.content.lower():
        user_text = message.content

        # Generate AI response
        reply = await generate_reply(user_text, target_user)

        await message.channel.send(reply)


    # let the bot process messages simultaneously
    await bot.process_commands(message)


web.keep_alive()
bot.run(token)
