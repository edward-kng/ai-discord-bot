import asyncio
import random

import discord

from discord_music_bot.logic.utils.music.music_fetcher import MusicFetcher
from discord_music_bot.logic.utils.music.song import Song
from collections import deque


class Session:
    def __init__(
        self,
        feedback_channel: discord.TextChannel,
        guild: discord.Guild,
        voice: discord.VoiceState,
        music_fetcher: MusicFetcher,
    ) -> None:
        self._feedback_channel = feedback_channel
        self._guild = guild
        self._voice = voice

        self._downloader = asyncio.create_task(self._start_downloader())
        self._player = asyncio.create_task(self._start_playback())

        self._download_queue: deque[Song] = deque()
        self._play_queue: deque[Song] = deque()

        self._active = True
        self._paused = False
        self._skipped = False
        self._now_playing = None

        self._download_ready = asyncio.Condition()
        self._playback_ready = asyncio.Condition()

        self._music_fetcher = music_fetcher

    async def enqueue(self, query: str, shuffle=False, pos=0, play_next=False) -> None:
        metadata_list = await asyncio.to_thread(self._get_metadata, query)

        if metadata_list is None:
            await self._feedback_channel.send(
                "Error: could not find song or invalid URL!"
            )

            return

        metadata_list = metadata_list[pos:]

        if shuffle:
            random.shuffle(metadata_list)

        if play_next:
            self._download_queue.extendleft(metadata_list)
            self._play_queue.extendleft(metadata_list)
        else:
            self._download_queue.extend(metadata_list)
            self._play_queue.extend(metadata_list)

        async with self._download_ready:
            self._download_ready.notify()

        msg = "Added to queue: "

        for i in range(min(3, len(metadata_list))):
            msg += "\n" + metadata_list[i].title

        if len(metadata_list) > 3:
            msg += "\n..."

        await self._feedback_channel.send(msg)

    async def skip(self) -> None:
        self._skipped = True
        self._paused = False

    async def quit(self) -> None:
        if self._voice.is_playing():
            self._voice.stop()

        await self._voice.disconnect()

        self._active = False

        async with self._playback_ready:
            self._playback_ready.notify()

        async with self._download_ready:
            self._download_ready.notify()

        await asyncio.gather(self._downloader, self._player)

    def get_song_queue(self) -> deque[Song]:
        return self._play_queue.copy()

    async def _start_downloader(self) -> None:
        while self._active:
            if len(self._download_queue) == 0:
                async with self._download_ready:
                    await self._download_ready.wait()

            if not self._active:
                break

            song = self._download_queue[0]

            if not song.audio:
                song.audio = await asyncio.to_thread(self._get_audio, song)

            if song == self._play_queue[0]:
                async with self._playback_ready:
                    self._playback_ready.notify()

            self._download_queue.popleft()

    def _get_metadata(self, query: str | discord.Attachment) -> list[Song]:
        if isinstance(query, discord.Attachment):
            return [Song(query, query.url, query.filename, "file")]

        return self._music_fetcher.get_metadata(query)

    def _get_audio(self, song: Song) -> str | None:
        return self._music_fetcher.get_audio(song)

    def pause_resume(self) -> None:
        self._paused = not self._paused

        if self._paused:
            self._voice.pause()
        else:
            self._voice.resume()

    def is_active(self) -> bool:
        return self._active

    def is_playing(self) -> bool:
        return self._voice.is_playing()

    def get_now_playing(self) -> str | None:
        if self._voice.is_playing():
            return self._now_playing

        return None

    async def _start_playback(self) -> None:
        while self._active:
            if len(self._play_queue) == 0 or not self._play_queue[0].audio:
                async with self._playback_ready:
                    await self._playback_ready.wait()

            if not self._active:
                break

            song = self._play_queue.popleft()
            self._voice.play(
                discord.FFmpegPCMAudio(
                    song.audio,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    options="-vn",
                )
            )

            await self._feedback_channel.send("Now playing: " + song.title)
            self._now_playing = song.title

            while self._active and (self._voice.is_playing() or self._paused):
                await asyncio.sleep(0.1)

                if self._skipped:
                    self._voice.stop()
                    self._skipped = False

                    break

            self._now_playing = None

            await asyncio.sleep(1)
