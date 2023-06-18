import asyncio
import openai

from .history import download_history


class ChatService:
    def __init__(self, bot):
        self.memory = 10
        self.bot = bot

    async def answer(self, channel, question):
        if not openai.api_key:
            return "Chat not enabled!"

        chat_history = await download_history(
            channel, limit=self.memory, download_images=False
        )

        return await asyncio.to_thread(
            self.create_completion, chat_history, question
        )

    def create_completion(self, chat_history, question):
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
                        "You are a Discord bot that chats with users. Your name is " + self.bot.user.name
                        + ". Below is a transcript of "
                        + "the conversation so far:\n" + history_prompt
                },
                {"role": "user", "content": question}
            ]
        )["choices"][0]["message"]["content"]
