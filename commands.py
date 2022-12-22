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
cached_songs = {}

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

    metadata = await asyncio.to_thread(get_metadata, song)

    if metadata is None:
        await channel.send("Error: could not find song or invalid URL!")

        return

    await channel.send("Added to queue: " + metadata["title"])

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
    
    guilds[guild].download_queue.append(
            (song, metadata["id"], metadata["title"]))

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
        msg += str(nr) + ". " + song + "\n"
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
        cache_dir = "cache/" + song[1]

        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        track_nr = 1
        download_status = set()
        download_thread = Thread(
            target = background_download, args = (
                song[0], cache_dir, download_status))
        download_thread.start()

        while len(download_status) == 0:
            await asyncio.sleep(0.1)

            for file in os.listdir(cache_dir):
                separator = file.index("_")

                if int(file[0:separator]) == track_nr and (
                        not ".part" in file):
                    file_path = cache_dir + "/" + file
                    track_nr += 1
                    guilds[guild].play_queue.append(file_path)
                    guilds[guild].downloaded_songs.append(file_path)

                    if file_path not in cached_songs:
                        cached_songs[file_path] = set()

                    # Add this guild to set of guilds that have requested this song
                    cached_songs[file_path].add(guild)

                    await guilds[guild].song_ready.acquire()

                    try:
                        guilds[guild].song_ready.notify()
                    finally:
                        guilds[guild].song_ready.release()

        guilds[guild].download_queue.pop(0)

    for song in guilds[guild].downloaded_songs:
        cached_songs[song].remove(guild)

        # If no other guild has requested this song, delete it from cache
        if len(cached_songs[song]) == 0:
            os.remove(song)

def get_metadata(song):
    if "youtube.com" in song:
        downloader = yt_dlp.YoutubeDL({})

        try:
            return downloader.extract_info(
                song, download = False, process = False)
        except:
            return None
    
    # Song is not a YouTube URL, use search or generic downloader
    else:
        downloader = yt_dlp.YoutubeDL({"default_search": "ytsearch"})

        try:
            return downloader.extract_info(song, download = False)
        except:
            return None

def background_download(song, cache_dir, download_status):
    downloader = yt_dlp.YoutubeDL({
        "format": "bestaudio", "outtmpl": cache_dir + "/%(autonumber)s_%(id)s",
        "default_search": "ytsearch"})
    
    downloader.download(song)
    download_status.add(0)

async def playback(voice, channel):
    guild = voice.guild

    while guilds[guild].active:
        if len(guilds[guild].play_queue) == 0:
            async with guilds[guild].song_ready:
                await guilds[guild].song_ready.wait()

        if not guilds[guild].active:
            break
            
        song = guilds[guild].play_queue.pop(0)
        voice.play(discord.FFmpegPCMAudio(song))
        
        # await channel.send("Now playing: " + song)

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
