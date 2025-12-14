import asyncio
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import web  # assuming your keep_alive.py or similar
from openai import OpenAI
import time

# Conversation state memory
conversations = {}  # {user_id: {"history": [...], "last_time": timestamp}}
CONVO_TIMEOUT = 45  # seconds


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


def is_active_conversation(user_id):
    if user_id not in conversations:
        return False
    return (time.time() - conversations[user_id]["last_time"]) < CONVO_TIMEOUT


def add_to_history(user_id, role, content):
    if user_id not in conversations:
        conversations[user_id] = {"history": [], "last_time": time.time()}
    conversations[user_id]["history"].append({"role": role, "content": content})
    conversations[user_id]["last_time"] = time.time()


def clear_conversation(user_id):
    if user_id in conversations:
        del conversations[user_id]


def is_calling_jarvis(text: str) -> bool:
    t = text.lower().strip()

    # direct name check (primary trigger)
    if "jarvis" in t:
        return True

    # natural-language calls (very forgiving)
    call_keywords = [
        "help me", "can you", "could you", "what is", "who is",
        "explain", "calculate", "solve", "tell me", "show me",
        "i need", "how do i", "what's", "whats", "who's", "whos"
    ]

    if any(k in t for k in call_keywords):
        return True

    return False



async def generate_reply(user_id, user_message, name):
    persona = load_jarvis_persona()

    # Build messages array
    messages = [{"role": "system", "content": persona}]

    # Add history IF active conversation
    if is_active_conversation(user_id):
        messages.extend(conversations[user_id]["history"])

    # Add new user message
    messages.append({"role": "user", "content": f"{user_message}"})

    # AI call
    response = ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )

    reply = response.choices[0].message.content.strip()

    # Save both the user's message & Jarvis reply to history
    add_to_history(user_id, "user", user_message)
    add_to_history(user_id, "assistant", reply)

    return reply

async def ai_reply(message):
    user_id = message.author.id
    content = message.content
    calling = is_calling_jarvis(content)
    active = is_active_conversation(user_id)

    # 1. If user calls Jarvis → start conversation
    if calling and not active:
        print("user called jarvis")
        reply = await generate_reply(user_id, content, message.author.name)
        conversations[user_id] = conversations.get(user_id, {"history": [], "last_time": time.time()})
        await message.channel.send(reply)
        return

    # 2. If conversation is active → continue conversation (no need to say jarvis again)
    # 2. If conversation is active
    if active:

        lowered = content.lower()

        # 1. If Jarvis is CLEARLY being called, continue
        if "jarvis" in lowered:
            print("continue the conversation")
            reply = await generate_reply(user_id, content, message.author.name)
            await message.channel.send(reply)
            return

        # 2. If message sounds like a question or task
        task_words = ["what", "how", "why", "calculate", "solve", "explain", "who", "where", "when", "?", "did"]
        if any(w in lowered for w in task_words):
            print("user continues the conversation with a question or task")
            reply = await generate_reply(user_id, content, message.author.name)
            await message.channel.send(reply)
            return

        # 3. If user actually mentions another user → end conversation
        if message.mentions:
            clear_conversation(user_id)
            print("user mentions someone → end conversation")
            return

        # 4. If message is casual chat → end conversation
        casual = ["lol", "lmao", "bro", "dude", "wtf", "nah", "ok", "fr", "ong"]
        if any(lowered.startswith(c) for c in casual):
            clear_conversation(user_id)
            print("user engaged in casual conversation, most likely with another player")
            return

        # otherwise: end conversation
        clear_conversation(user_id)
        return


@bot.event
async def on_ready():
    print("Hello, I am J.A.R.V.I.S.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name != "╰‿╯-jarvis-spam":
        return

    # Responsive AI
    await ai_reply(message)



    await bot.process_commands(message)


web.keep_alive()
bot.run(token)
