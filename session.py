import asyncio
import discord
import os
import random
from spotify import Spotify
from youtube_generic import YouTubeGeneric

class Session:
    cached_songs = {}

    def __init__(self, feedback_channel, guild, voice):
        self._feedback_channel = feedback_channel
        self._guild = guild
        self._voice = voice

        self._downloader = asyncio.create_task(self._start_downloader())
        self._playback = asyncio.create_task(self._start_playback())
        self._idle_timer = asyncio.create_task(self._start_idle_timer())

        self._download_queue = []
        self._downloaded_songs = []
        self._play_queue = []

        self._active = True
        self._paused = False
        self._skipped = False

        self._download_ready = asyncio.Condition()
        self._playback_ready = asyncio.Condition()

    async def enqueue(self, song, shuffle = False):
        metadata_list = await asyncio.to_thread(Session._get_metadata, song)

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
            self._downloader, self._playback, self._idle_timer)

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
            song_path = "cache/" + song["id"]

            await asyncio.to_thread(
                Session._download_song, song, song_path)

            self._play_queue.append({
                "file": song_path, "title": song["title"]})
            self._downloaded_songs.append(song_path)

            if song_path not in Session.cached_songs:
                Session.cached_songs[song_path] = set()

            # Add this guild to set of guilds that have requested this song
            Session.cached_songs[song_path].add(self._guild)

            async with self._playback_ready:
                self._playback_ready.notify()

            self._download_queue.pop(0)

        for song in self._downloaded_songs:
            Session.cached_songs[song].remove(self._guild)

            # If no other guild has requested this song, delete it from cache
            if len(Session.cached_songs[song]) == 0:
                os.remove(song)

    def _get_metadata(query):
        if "spotify.com" in query:
            return Spotify.get_metadata(query)
        
        return YouTubeGeneric.get_metadata(query)

    def _download_song(song, location):
        if song["type"] == "song_spotify":
            Spotify.download(song, location)
        elif song["type"] == "song_youtube_generic":
            YouTubeGeneric.download(song, location)

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
            self._voice.play(discord.FFmpegPCMAudio(song["file"]))
            
            await self._feedback_channel.send("Now playing: " + song["title"])

            while not self._skipped and self._active and (
                        self._voice.is_playing() or self._paused):
                await asyncio.sleep(0.1)
            
            if self._skipped:
                self._voice.stop()
                self._skipped = False
                
            await asyncio.sleep(1)
