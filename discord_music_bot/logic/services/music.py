import asyncio

import discord

from discord_music_bot.logic.utils.music.session import Session
from ..utils.music.music_fetcher import MusicFetcher
from ...presentation.bot import Bot


class MusicService:
    def __init__(self, bot: Bot, music_fetcher: MusicFetcher) -> None:
        self._bot = bot
        self._music_fetcher = music_fetcher
        self._sessions = {}

    async def enqueue_song(
        self,
        query: str,
        pos: int,
        user: discord.User | discord.Member,
        guild: discord.Guild,
        channel: discord.TextChannel,
        shuffle=False,
    ) -> str:
        user_voice = user.voice

        if not user_voice and guild not in self._sessions:
            return "Join a voice channel first!"

        msg = query

        if guild not in self._sessions:
            await user_voice.channel.connect()

            voice = discord.utils.get(self._bot.voice_clients, guild=guild)
            self._sessions[guild] = Session(channel, guild, voice, self._music_fetcher)

            asyncio.create_task(self.start_idle_timer(guild))

        asyncio.create_task(
            self._sessions[guild].enqueue(query=query, pos=pos, shuffle=shuffle)
        )

        return msg

    async def skip_song(self, guild: discord.Guild) -> str:
        if guild in self._sessions:
            await self._sessions[guild].skip()

            return "Skipped!"
        else:
            return "Not in a voice channel!"

    async def leave(self, guild: discord.Guild) -> str:
        if guild in self._sessions:
            msg = "Bye!"

            await self._sessions[guild].quit()

            self._sessions.pop(guild)
        else:
            msg = "Not in a voice channel!"

        return msg

    def pause_song(self, guild: discord.Guild) -> str:
        if guild in self._sessions:
            self._sessions[guild].pause_resume()
            return "Paused!"

        return "Not in a voice channel!"

    def resume_song(self, guild: discord.Guild) -> str:
        if guild in self._sessions:
            self._sessions[guild].pause_resume()
            return "Resumed!"

        return "Not in a voice channel!"

    def get_song_queue(self, guild: discord.Guild) -> str:
        if guild in self._sessions:
            song_queue = self._sessions[guild].get_song_queue()

            if len(song_queue) > 10:
                msg = "Next 10 song in queue:"

                for i in range(10):
                    msg += "\n" + str(i + 1) + ". " + song_queue[i]["title"]
            else:
                msg = "Queue:"

                for i in range(len(song_queue)):
                    msg += "\n" + str(i + 1) + ". " + song_queue[i]["title"]

            return msg
        return "No songs queued!"

    def get_now_playing_song(self, guild: discord.Guild) -> str:
        if guild in self._sessions:
            song = self._sessions[guild].get_now_playing()

            if song is not None:
                return "Now playing: " + song

        return "No song playing!"

    async def start_idle_timer(self, guild: discord.Guild) -> None:
        session = self._sessions[guild]

        while session.is_active():
            idle_secs = 0

            await asyncio.sleep(0.1)

            while not session.is_playing() and session.is_active():
                await asyncio.sleep(1)

                idle_secs += 1

                if idle_secs >= 300:
                    await session.quit()

                    self._sessions.pop(guild)
