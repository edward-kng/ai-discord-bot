import asyncio
import json
from threading import Thread

import discord
import requests
from openai import OpenAI

from .music import MusicService
from discord_music_bot.logic.utils.chat.chat import (
    download_history,
    export_history,
    parse_message,
)
from ...presentation.bot import Bot

functions = [
    {
        "name": "send_direct_message",
        "description": "Send a direct message to a user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user, usually found after an @ symbol.",
                },
                "message": {"type": "string", "description": "Message to send."},
            },
            "required": ["user_id", "message"],
        },
    },
    {
        "name": "export_chat_history",
        "description": "Back up and export the chat history",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "enqueue_song",
        "description": "Enqueue a song to play",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Song URL or search query.",
                },
                "shuffle": {
                    "type": "boolean",
                    "description": """Whether to shuffle the requested 
                    playlist of songs. Has no effect on single songs. Defaults 
                    to false.""",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "skip_song",
        "description": "Skip the current song",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_now_playing_song",
        "description": "Get the name and artist of the current song playing",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "pause_song",
        "description": "Pause the current song",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "resume_song",
        "description": "Resume the current song",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_song_queue",
        "description": "The the current queue of songs to play",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "leave",
        "description": "Leave the voice chat and stop all playing music",
        "parameters": {"type": "object", "properties": {}},
    },
]


class ChatService:
    def __init__(
        self, bot: Bot, openai_client: OpenAI, music_service: MusicService
    ) -> None:
        self.memory = 10
        self.bot = bot
        self._music_service = music_service
        self._openai_client = openai_client

    async def answer(
        self,
        channel: discord.TextChannel,
        question: str,
        user: discord.User | discord.Member,
        guild: discord.Guild,
    ) -> str:
        if not self._openai_client:
            return "Chat not enabled!"

        chat_history = await self.get_chat_thread(channel)

        async with channel.typing():
            return await self.create_completion(
                chat_history, question, user, guild, channel
            )

    async def dm_user(self, user_id: int, msg: str) -> None:
        user = await self.bot.fetch_user(user_id)
        await user.send(msg)

    async def create_completion(
        self,
        chat_history: dict,
        question: str,
        user: discord.User | discord.Member,
        guild: discord.Guild,
        channel: discord.TextChannel,
    ) -> str:
        history_prompt = ""
        chat_history["messages"].pop(0)

        for message in reversed(chat_history["messages"]):
            history_prompt += (
                message["sender"]["name"] + " said: " + message["messageContent"] + "\n"
            )

        print(history_prompt)
        return "TESTING"

        data = await asyncio.to_thread(
            self._openai_client.chat.completions.create,
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Discord bot that chats with users. Your name is "
                    + self.bot.user.name
                    + ". Below is a transcript of "
                    + "the conversation so far:\n"
                    + history_prompt,
                },
                {"role": "user", "content": question},
            ],
            functions=functions,
        )

        data = data.choices[0]
        msg = data.message.content
        call = data.message.function_call

        if call:
            args = json.loads(call.arguments)
            fun = call.name

            if fun == "send_direct_message":
                await self.dm_user(args["user_id"], args["message"])
                msg = "Okay!"
            elif fun == "export_chat_history":
                msg = "Okay! Just a moment."
                asyncio.create_task(export_history(channel))
            elif fun == "enqueue_song":
                msg = await self._music_service.enqueue_song(
                    args["query"],
                    0,
                    user,
                    guild,
                    channel,
                    args["shuffle"] if "shuffle" in args else False,
                )
            elif fun == "get_now_playing_song":
                msg = self._music_service.get_now_playing_song(guild)
            elif fun == "skip_song":
                msg = await self._music_service.skip_song(guild)
            elif fun == "pause_song":
                msg = self._music_service.pause_song(guild)
            elif fun == "resume_song":
                msg = self._music_service.resume_song(guild)
            elif fun == "get_song_queue":
                msg = self._music_service.get_song_queue(guild)
            else:
                msg = await self._music_service.leave(guild)

        return msg

    async def get_chat_thread(self, channel: discord.TextChannel):
        path = "chat-history/" + str(channel.id)
        history = {"messages": []}

        async for message in channel.history():
            history["messages"].append(parse_message(message, [], path, False))

            if self.bot.mentions(message):
                break

        return history
