import asyncio
import discord
import os
import yt_dlp
from bot import Bot
from guild import Guild

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

    if voice is None:
        voice = await user_connected.channel.connect()
        
        guilds[guild] = Guild()
        guilds[guild].download_task = asyncio.create_task(
            download(guild, channel))
        guilds[guild].playback_task = asyncio.create_task(
            playback(voice, channel))

    await interaction.response.send_message("Added to queue: " + song)
    
    await guilds[guild].download_ready.acquire()
    
    await guilds[guild].lock.acquire()
    
    try:
        guilds[guild].download_queue.append(song)
        guilds[guild].download_ready.notify()
    finally:
        guilds[guild].download_ready.release()
        guilds[guild].lock.release()

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
async def say(interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

async def download(guild, channel):
    while guilds[guild].active:
        if len(guilds[guild].download_queue) == 0:
            async with guilds[guild].download_ready:
                await guilds[guild].download_ready.wait()

        if not guilds[guild].active:
            break

        async with guilds[guild].lock:
            song_link = guilds[guild].download_queue.pop(0)
            metadata = await asyncio.to_thread(get_metadata, song_link)

            if metadata is None:
                await channel.send(
                    "Could not download: " + song_link + ", invalid URL or song not found!")
            
            # Check if URL is a playlist, then add each song to the download queue
            elif "entries" in metadata:
                for song in metadata["entries"]:
                    guilds[guild].download_queue.append(song["original_url"])
            else:
                song = await asyncio.to_thread(background_download, song_link)
                
                guilds[guild].play_queue.append(("cache/" + song, song_link))
                
                if song not in cached_songs:
                    cached_songs[song] = set()

                guilds[guild].downloaded_songs.append(song)

                # Add this guild to set of guilds that have requested this song
                cached_songs[song].add(guild)

                await guilds[guild].song_ready.acquire()

                try:
                    guilds[guild].song_ready.notify_all()
                finally:
                    guilds[guild].song_ready.release()
        
    for song in guilds[guild].downloaded_songs:
        cached_songs[song].remove(guild)

        # If no other guild has requested this song, delete it from cache
        if len(cached_songs[song]) == 0:
            os.remove("cache/" + song)

def get_metadata(song):
    downloader = yt_dlp.YoutubeDL({
        "format": "bestaudio", "outtmpl": "cache/%(id)s", "default_search": "ytsearch"})

    try:
        return downloader.extract_info(song, download = False)
    except:
        return None

def background_download(song):
    downloader = yt_dlp.YoutubeDL({
        "format": "bestaudio", "outtmpl": "cache/%(id)s", "default_search": "ytsearch"})
    
    metadata = downloader.extract_info(song)
    
    return metadata["id"]

async def playback(voice, channel):
    guild = voice.guild

    while guilds[guild].active:
        if len(guilds[guild].play_queue) == 0:
            async with guilds[guild].song_ready:
                await guilds[guild].song_ready.wait()

        if not guilds[guild].active:
            break
            
        song = guilds[guild].play_queue.pop(0)
        voice.play(discord.FFmpegPCMAudio(song[0]))
        
        await channel.send("Now playing: " + song[1])

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
