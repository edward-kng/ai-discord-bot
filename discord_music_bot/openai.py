import asyncio

import openai

from discord_music_bot.history import download_history


async def answer(channel, question, name, memory):

    if not openai.api_key:
        return "Chat not enabled!"

    chat_history = await download_history(channel, limit=memory, download_images=False)

    return await asyncio.to_thread(create_completion, chat_history, question, name)


def create_completion(chat_history, question, name):
    history_prompt = ""
    chat_history["messages"].pop(0)

    for message in reversed(chat_history["messages"]):
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
