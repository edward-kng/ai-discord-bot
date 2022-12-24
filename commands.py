import asyncio
import discord
import os
import yt_dlp
from bot import Bot
from guild import Guild
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(intents)
guilds = {}

@bot.tree.command()
async def play(interaction: discord.Interaction, song: str):
    user_connected = interaction.user.voice
    guild = interaction.guild
    channel = interaction.channel
    voice = discord.utils.get(bot.voice_clients, guild = guild)

    if not user_connected and voice is None:
        await interaction.response.send_message("Join a voice channel first!")
        
        return

    await interaction.response.send_message("Searching for song...")

    metadata_list = await asyncio.to_thread(get_metadata, song)

    if metadata_list is None:
        await channel.send("Error: could not find song or invalid URL!")

        return

    msg = "Added to queue: "

    for metadata in metadata_list:
        msg += "\n" + metadata[2]

    await channel.send(msg)

    if voice is None:
        voice = await user_connected.channel.connect()
        
        guilds[guild] = Guild()
        guilds[guild].download_task = asyncio.create_task(
            download(guild))
        guilds[guild].playback_task = asyncio.create_task(
            playback(voice, channel))
        guilds[guild].idle_task = asyncio.create_task(
            idle_timeout(guild, voice)
        )
    
    guilds[guild].download_queue.extend(metadata_list)

    await guilds[guild].download_ready.acquire()
    
    try:
        guilds[guild].download_ready.notify()
    finally:
        guilds[guild].download_ready.release()

@bot.tree.command()
async def skip(interaction: discord.Interaction):
    guild = interaction.guild
    voice = discord.utils.get(bot.voice_clients, guild = guild)

    if voice is not None:
        guilds[guild].skipped = True

        await interaction.response.send_message("Skipped!")
    else:
        await interaction.response.send_message("No music playing!")

@bot.tree.command()
async def leave(interaction: discord.Interaction):
    guild = interaction.guild
    voice = discord.utils.get(bot.voice_clients, guild = guild)

    if voice is not None:
        voice.stop()
        
        await voice.disconnect()
        
        guilds[guild].active = False
        
        async with guilds[guild].song_ready:
            guilds[guild].song_ready.notify()
        
        await interaction.response.send_message("Bye!")
    else:
        await interaction.response.send_message("Not in a voice channel!")

@bot.tree.command()
async def pause(interaction: discord.Interaction):
    guild = interaction.guild
    voice = discord.utils.get(bot.voice_clients, guild = guild)
    guilds[guild].paused = True
    voice.pause()

    await interaction.response.send_message("Paused!")

@bot.tree.command()
async def resume(interaction: discord.Interaction):
    guild = interaction.guild
    voice = discord.utils.get(bot.voice_clients, guild = guild)
    guilds[guild].paused = False
    voice.resume()

    await interaction.response.send_message("Resumed!")

@bot.tree.command()
async def queue(interaction: discord.Interaction):
    guild = interaction.guild
    
    if guild not in guilds or not guilds[guild].active:
        await interaction.response.send_message("No music playing!")

        return
    
    msg = "Queue:\n"
    nr = 1

    for song in guilds[guild].play_queue:
        msg += str(nr) + ". " + song["title"] + "\n"
        nr += 1

    for song in guilds[guild].download_queue:
        msg += str(nr) + ". " + song[2] + "\n"
        nr += 1

    await interaction.response.send_message(msg)

@bot.tree.command()
async def say(interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

async def download(guild):
    while guilds[guild].active:
        if len(guilds[guild].download_queue) == 0:
            async with guilds[guild].download_ready:
                await guilds[guild].download_ready.wait()

        if not guilds[guild].active:
            break

        song = guilds[guild].download_queue[0]
        song_path = "cache/" + song[1]

        await asyncio.to_thread(background_download, song[0], song_path)

        guilds[guild].play_queue.append({
            "file": song_path, "title": song[2]})
        guilds[guild].downloaded_songs.append(song_path)

        if song_path not in Guild.cached_songs:
            Guild.cached_songs[song_path] = set()

        # Add this guild to set of guilds that have requested this song
        Guild.cached_songs[song_path].add(guild)

        await guilds[guild].song_ready.acquire()

        try:
            guilds[guild].song_ready.notify()
        finally:
            guilds[guild].song_ready.release()

        guilds[guild].download_queue.pop(0)

    for song in guilds[guild].downloaded_songs:
        Guild.cached_songs[song].remove(guild)

        # If no other guild has requested this song, delete it from cache
        if len(Guild.cached_songs[song]) == 0:
            os.remove(song)

def get_metadata(song):
    track_list = []

    if "spotify.com" in song:
        if Guild.spotify_client is None:
            return None
        if "playlist" in song:
            playlist = Guild.spotify_client.playlist_tracks(song)
            for track in playlist["items"]:
                title = ""

                for artist in track["track"]["album"]["artists"]:
                        title += artist["name"] + " "

                title += "- " + track["track"]["name"]

                track_list.append(title + " AUDIO", track["track"]["id"], title)
        elif "album" in song:
            album = Guild.spotify_client.album_tracks(song)

            for track in album["items"]:
                title = ""

                for artist in track["artists"]:
                    title += artist["name"] + " "

                title += "- " + track["name"]

                track_list.append((title + " AUDIO", track["id"], title))
        else:
            track = Guild.spotify_client.track(song)

            title = ""

            for artist in track["album"]["artists"]:
                    title += artist["name"] + " "

            title += "- " + track["name"]

            track_list.append((title + " AUDIO", track["id"], title))
    elif "youtube.com" in song:
        downloader = yt_dlp.YoutubeDL({})

        try:
            metadata = downloader.extract_info(
                song, download = False, process = False)
        except:
            return None

        if "entries" in metadata:
            for entry in metadata["entries"]:
                track_list.append((entry["url"], entry["id"], entry["title"]))
        else:
            track_list.append((song, metadata["id"], metadata["title"]))
    
    # Song is not a YouTube or Spotify URL, use search or generic downloader
    else:
        downloader = yt_dlp.YoutubeDL({"default_search": "ytsearch"})

        try:
            metadata = downloader.extract_info(song, download = False)

        except:
            return None

        result = metadata["entries"][0]
        track_list.append((song, result["id"], result["title"]))

    return track_list

def background_download(song, location):
    downloader = yt_dlp.YoutubeDL({
        "format": "bestaudio", "outtmpl": location,
        "default_search": "ytsearch", "noplaylist": True})
    
    downloader.download(song)

async def playback(voice, channel):
    guild = voice.guild

    while guilds[guild].active:
        if len(guilds[guild].play_queue) == 0:
            async with guilds[guild].song_ready:
                await guilds[guild].song_ready.wait()

        if not guilds[guild].active:
            break
            
        song = guilds[guild].play_queue.pop(0)
        voice.play(discord.FFmpegPCMAudio(song["file"]))
        
        await channel.send("Now playing: " + song["title"])

        while not guilds[guild].skipped and guilds[guild].active and (
                    voice.is_playing() or guilds[guild].paused):
            await asyncio.sleep(1)
        
        if guilds[guild].skipped:
            voice.stop()

        guilds[guild].skipped = False
    

    # Playback stopped, notify download task to stop waiting for more songs
    await guilds[guild].download_ready.acquire()

    try:
        guilds[guild].download_ready.notify_all()
    finally:
        guilds[guild].download_ready.release()

async def idle_timeout(guild, voice):
    while guilds[guild].active:
        idle_secs = 0

        await asyncio.sleep(0)

        while not voice.is_playing() and guilds[guild].active:
            await asyncio.sleep(1)
            
            idle_secs += 1

            if idle_secs >= 300:
                await voice.disconnect()
        
                guilds[guild].active = False
                
                async with guilds[guild].song_ready:
                    guilds[guild].song_ready.notify()
