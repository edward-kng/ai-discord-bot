import asyncio

import openai
from os import getenv


async def answer(question, name):
    api_key = getenv("OPENAI_API_KEY")

    if api_key:
        openai.api_key = api_key
    else:
        return "Chat not enabled!"

    return await asyncio.to_thread(create_completion, question, name)


def create_completion(question, name):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Discord bot that chats with users. Your name is " + name + "."},
            {"role": "user", "content": question}
        ]
    )["choices"][0]["message"]["content"]
