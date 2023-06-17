import asyncio

import openai

from discord_music_bot.history import download_history


def create_completion(chat_history, question, bot):
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
                    "You are a Discord bot that chats with users. Your name is " + bot.user.name + ". Below is a transcript of "
                + "the conversation so far:\n" + history_prompt
            },
            {"role": "user", "content": question}
        ]
    )["choices"][0]["message"]["content"]


class ChatService:
    def __init__(self, name):
        self.memory = 10
        self.name = name

    async def answer(self, channel, question):

        if not openai.api_key:
            return "Chat not enabled!"

        chat_history = await download_history(channel, limit=self.memory, download_images=False)

        return await asyncio.to_thread(create_completion, chat_history, question, self.name)
