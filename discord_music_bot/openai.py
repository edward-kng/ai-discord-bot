import asyncio

import openai
from os import getenv

from discord_music_bot.history import export_history


async def answer(channel, question, name, memory):
    api_key = getenv("OPENAI_API_KEY")

    if api_key:
        openai.api_key = api_key
    else:
        return "Chat not enabled!"

    chat_history = await export_history(channel, limit=memory, download_images=False)

    return await asyncio.to_thread(create_completion, chat_history, question, name)


def create_completion(chat_history, question, name):
    history_prompt = ""

    for message in chat_history["messages"]:
        history_prompt += message["sender"]["name"] + " said: " + message["messageContent"] + "\n"

    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content":
                    "You are a Discord bot that chats with users. Your name is " + name + ". Below is a transcript of "
                + "the conversation so far:\n" + history_prompt
            },
            {"role": "user", "content": question}
        ]
    )["choices"][0]["message"]["content"]
