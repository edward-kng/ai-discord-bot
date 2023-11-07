import asyncio
import discord
from ..session import Session
from ..idle_timer import start_idle_timer

class MusicService:
    def __init__(self, bot, spotify):
        self._bot = bot
        self._spotify = spotify
        self._sessions = {}
        self._idle_timers = set()

    async def enqueue_song(self, query, pos, user, guild, channel, shuffle=False):
        user_voice = user.voice

        if not user_voice and guild not in self._sessions:
            return "Join a voice channel first!"

        msg = query

        if guild not in self._sessions:
            await user_voice.channel.connect()

            voice = discord.utils.get(self._bot.voice_clients, guild=guild)
            self._sessions[guild] = Session(channel, guild, voice, self._spotify)

            self._idle_timers.add(
                asyncio.create_task(start_idle_timer(self._sessions, guild)))

        asyncio.create_task(self._sessions[guild].enqueue(query=query, pos=pos, shuffle=shuffle))

        return msg

    async def skip_song(self, guild):
        if guild in self._sessions:
            await self._sessions[guild].skip()

            return "Skipped!"
        else:
            return "Not in a voice channel!"
        
    async def leave(self, guild):
        if guild in self._sessions:
            msg = "Bye!"

            await self._sessions[guild].quit()

            self._sessions.pop(guild)
        else:
            msg = "Not in a voice channel!"

        return msg
    
    def pause_song(self, guild):
        if guild in self._sessions:
            self._sessions[guild].pause_resume()
            return "Paused!"
        
        return "Not in a voice channel!"
    
    def resume_song(self, guild):
        if guild in self._sessions:
            self._sessions[guild].pause_resume()
            return "Resumed!"
        
        return "Not in a voice channel!"
    
    def get_song_queue(self, guild):
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

    def get_now_playing_song(self, guild):
        if guild in self._sessions:
            song = self._sessions[guild].get_now_playing()

            if song is not None:
                return "Now playing: " + song

        return "No song playing!"
