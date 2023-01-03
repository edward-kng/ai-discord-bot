import asyncio
import discord
import random
from discord_music_bot.downloaders.spotify import Spotify
from discord_music_bot.downloaders.youtube_generic import YouTubeGeneric

class Session:
    def __init__(self, feedback_channel, guild, voice):
        self._feedback_channel = feedback_channel
        self._guild = guild
        self._voice = voice

        self._downloader = asyncio.create_task(self._start_downloader())
        self._player = asyncio.create_task(self._start_playback())
        self._idle_timer = asyncio.create_task(self._start_idle_timer())

        self._download_queue = []
        self._play_queue = []

        self._active = True
        self._paused = False
        self._skipped = False

        self._download_ready = asyncio.Condition()
        self._playback_ready = asyncio.Condition()

    async def enqueue(self, query, shuffle = False):
        metadata_list = await asyncio.to_thread(Session._get_metadata, query)

        if metadata_list is None:
            await self._feedback_channel.send(
                "Error: could not find song or invalid URL!")

            return

        if shuffle:
            random.shuffle(metadata_list)

        self._download_queue.extend(metadata_list)

        async with self._download_ready:
            self._download_ready.notify()

        msg = "Added to queue: "

        for i in range(min(3, len(metadata_list))):
            msg += "\n" + metadata_list[i]["title"]

        if len(metadata_list) > 3:
            msg += "\n..."

        await self._feedback_channel.send(msg)

    async def skip(self):
        self._skipped = True
        self._paused = False

    async def quit(self):
        if self._voice.is_playing():
            self._voice.stop()
        
        await self._voice.disconnect()

        self._active = False

        async with self._playback_ready:
            self._playback_ready.notify()

        async with self._download_ready:
            self._download_ready.notify()

        await asyncio.gather(
            self._downloader, self._player, self._idle_timer)

    def get_song_queue(self):
        return self._play_queue + self._download_queue

    async def _start_idle_timer(self):
        while self._active:
            idle_secs = 0

            await asyncio.sleep(0.1)

            while not self._voice.is_playing() and self._active:
                await asyncio.sleep(1)
                
                idle_secs += 1

                if idle_secs >= 300:
                    await self.quit()

    async def _start_downloader(self):
        while self._active:
            if len(self._download_queue) == 0:
                async with self._download_ready:
                    await self._download_ready.wait()

            if not self._active:
                break

            song = self._download_queue[0]

            if "audio" not in song:
                song["audio"] = await asyncio.to_thread(
                    Session._get_audio, song)

            self._play_queue.append(song)

            async with self._playback_ready:
                self._playback_ready.notify()

            self._download_queue.pop(0)

    def _get_metadata(query):
        if "spotify.com" in query:
            return Spotify.get_metadata(query)
        
        return YouTubeGeneric.get_metadata(query)

    def _get_audio(song):
        if song["type"] == "spotify":
            return Spotify.get_audio(song)
        elif song["type"] == "youtube_generic":
            return YouTubeGeneric.get_audio(song)

    def pause_resume(self):
        self._paused = not self._paused

        if self._paused:
            self._voice.pause()
        else:
            self._voice.resume()

    async def _start_playback(self):
        while self._active:
            if len(self._play_queue) == 0:
                async with self._playback_ready:
                    await self._playback_ready.wait()

            if not self._active:
                break
                
            song = self._play_queue.pop(0)
            self._voice.play(discord.FFmpegPCMAudio(song["audio"]))
            
            await self._feedback_channel.send("Now playing: " + song["title"])

            while self._active and (self._voice.is_playing() or self._paused):
                await asyncio.sleep(0.1)
            
                if self._skipped:
                    self._voice.stop()
                    self._skipped = False

                    break
                
            await asyncio.sleep(1)
