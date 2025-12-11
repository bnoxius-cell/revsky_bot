import asyncio
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import web  # assuming your keep_alive.py or similar
from openai import OpenAI

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)
ai = OpenAI(api_key=OPENAI_API_KEY)

def load_jarvis_persona(filepath="jarvis_persona.txt"):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def is_calling_jarvis(text: str) -> bool:
    """
    Returns True if the user is clearly addressing Jarvis,
    not just mentioning the name in a sentence.
    """

    text = text.lower().strip()

    # Patterns that strongly indicate the bot is being addressed
    call_phrases = [
        "jarvis,",          # "Jarvis, help me"
        "hey jarvis",       # "hey jarvis what's up?"
        "ok jarvis",
        "okay jarvis",
        "yo jarvis",
        "hi jarvis",
        "hello jarvis",
    ]

    # If message *starts* with his name, it's almost always a direct call
    if text.startswith("jarvis"):
        return True

    # Check phrase-based invocation
    for phrase in call_phrases:
        if phrase in text:
            return True

    # Check if the name appears before a request verb
    # Example: "dang jarvis can you help me?"
    request_verbs = ["help", "tell", "explain", "do", "make", "check", "can you", "could you"]

    if "jarvis" in text:
        for verb in request_verbs:
            if verb in text and text.index("jarvis") < text.index(verb):
                return True

    # If none of the above match, it's probably casual mention
    return False


async def generate_reply(user_message, pronoun):
    persona = load_jarvis_persona()
    # Compose messages array for chat completion
    messages = [
        {"role": "system", "content": persona},
        {"role": "user", "content": f"{user_message}\n(Refer to user as {pronoun})."}
    ]
    response = ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

@bot.event
async def on_ready():
    print("Hello, I am J.A.R.V.I.S.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Analyze intent
    if is_calling_jarvis(message.content):
        reply = await generate_reply(message.content, message.author.name)
        await message.channel.send(reply)

    await bot.process_commands(message)

web.keep_alive()
bot.run(token)
