import asyncio
import discord
import os
import random
import yt_dlp

class Session:
    spotify_client = None
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
        metadata_list = await asyncio.to_thread(Session.get_metadata, song)

        if metadata_list is None:
            await self._feedback_channel.send(
                "Error: could not find song or invalid URL!")

            return

        if shuffle:
            random.shuffle(metadata_list)

        self._download_queue.extend(metadata_list)

        await self._download_ready.acquire()

        try:
            self._download_ready.notify()
        finally:
            self._download_ready.release()

        msg = "Added to queue: "

        for i in range(3):
            msg += "\n" + metadata_list[i]["title"]

        if len(metadata_list) > 3:
            msg += "\n..."

        await self._feedback_channel.send(msg)

    async def skip(self):
        self._skipped = True

    async def quit(self):
        if self._voice.is_playing():
            self._voice.stop()
        
        await self._voice.disconnect()

        self._active = False

        await self._playback_ready.acquire()

        try:
            self._playback_ready.notify()
        finally:
            self._playback_ready.release()

        await self._download_ready.acquire()

        try:
            self._download_ready.notify()
        finally:
            self._download_ready.release()

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
                Session.download_song, song["src"], song_path)

            self._play_queue.append({
                "file": song_path, "title": song["title"]})
            self._downloaded_songs.append(song_path)

            if song_path not in Session.cached_songs:
                Session.cached_songs[song_path] = set()

            # Add this guild to set of guilds that have requested this song
            Session.cached_songs[song_path].add(self._guild)

            await self._playback_ready.acquire()

            try:
                self._playback_ready.notify()
            finally:
                self._playback_ready.release()

            self._download_queue.pop(0)

        for song in self._downloaded_songs:
            Session.cached_songs[song].remove(self._guild)

            # If no other guild has requested this song, delete it from cache
            if len(Session.cached_songs[song]) == 0:
                os.remove(song)

    def get_metadata(song):
        track_list = []

        if "spotify.com" in song:
            if Session.spotify_client is None:
                return None
            if "playlist" in song:
                playlist = Session.spotify_client.playlist_tracks(song)
                
                for track in playlist["items"]:
                    title = ""

                    for artist in track["track"]["album"]["artists"]:
                            title += artist["name"] + " "

                    title += "- " + track["track"]["name"]

                    track_list.append({
                        "src": title + " AUDIO",
                        "id": track["track"]["id"], "title": title})
            elif "album" in song:
                album = Session.spotify_client.album_tracks(song)

                for track in album["items"]:
                    title = ""

                    for artist in track["artists"]:
                        title += artist["name"] + " "

                    title += "- " + track["name"]

                    track_list.append({
                        "src": title + " AUDIO",
                        "id": track["id"], "title": title})
            else:
                track = Session.spotify_client.track(song)

                title = ""

                for artist in track["album"]["artists"]:
                        title += artist["name"] + " "

                title += "- " + track["name"]

                track_list.append({
                        "src": title + " AUDIO",
                        "id": track["id"], "title": title})
        elif "youtube.com" in song:
            ytdl = yt_dlp.YoutubeDL({})

            try:
                metadata = ytdl.extract_info(
                    song, download = False, process = False)
            except:
                return None

            if "entries" in metadata:
                for entry in metadata["entries"]:
                    track_list.append({
                        "src": entry["url"], "id": entry["id"],
                        "title": entry["title"]})
            else:
                track_list.append({
                        "src": song, "id": metadata["id"],
                        "title": metadata["title"]})
        
        # Song is not a YouTube or Spotify URL, use search or generic downloader
        else:
            ytdl = yt_dlp.YoutubeDL({"default_search": "ytsearch"})

            try:
                metadata = ytdl.extract_info(song, download = False)

            except:
                return None

            result = metadata["entries"][0]
            track_list.append({
                        "src": song, "id": result["id"],
                        "title": result["title"]})

        return track_list

    def download_song(song, location):
        ytdl = yt_dlp.YoutubeDL({
            "format": "bestaudio", "outtmpl": location,
            "default_search": "ytsearch", "noplaylist": True})

        ytdl.download(song)

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
