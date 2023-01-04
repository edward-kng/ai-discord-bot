import asyncio
import discord
from discord_music_bot.bot import Bot
from discord_music_bot.idle_timer import start_idle_timer
from discord_music_bot.session import Session

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(intents)
sessions = {}
idle_timers = set()


@bot.tree.command()
async def play(interaction: discord.Interaction, song: str):
    user_voice = interaction.user.voice
    guild = interaction.guild

    if not user_voice and guild not in sessions:
        await interaction.response.send_message("Join a voice channel first!")
        
        return

    await interaction.response.send_message(song)

    if guild not in sessions:
        await user_voice.channel.connect()

        voice = discord.utils.get(bot.voice_clients, guild=guild)
        sessions[guild] = Session(interaction.channel, guild, voice)

        idle_timers.add(
            asyncio.create_task(start_idle_timer(sessions, guild)))

    await sessions[guild].enqueue(song)


@bot.tree.command()
async def play_file(
        interaction: discord.Interaction, file: discord.Attachment):
    user_voice = interaction.user.voice
    guild = interaction.guild

    if not user_voice and guild not in sessions:
        await interaction.response.send_message("Join a voice channel first!")
        
        return

    await interaction.response.send_message(file.filename)

    if guild not in sessions:
        await user_voice.channel.connect()

        voice = discord.utils.get(bot.voice_clients, guild=guild)
        sessions[guild] = Session(interaction.channel, guild, voice)

    await sessions[guild].enqueue(file)


@bot.tree.command()
async def shuffle(interaction: discord.Interaction, song: str):
    user_voice = interaction.user.voice
    guild = interaction.guild

    if not user_voice and guild not in sessions:
        await interaction.response.send_message("Join a voice channel first!")
        
        return

    await interaction.response.send_message(song)

    if guild not in sessions:
        await user_voice.channel.connect()

        voice = discord.utils.get(bot.voice_clients, guild=guild)
        sessions[guild] = Session(interaction.channel, guild, voice)

    await sessions[guild].enqueue(song, True)


@bot.tree.command()
async def skip(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await sessions[guild].skip()

        await interaction.response.send_message("Skipped!")
    else:
        await interaction.response.send_message("Not in a voice channel!")


@bot.tree.command()
async def leave(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await interaction.response.send_message("Bye!")

        await sessions[guild].quit()

        sessions.pop(guild)
    else:
        await interaction.response.send_message("Not in a voice channel!")


@bot.tree.command()
async def pause(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await interaction.response.send_message("Paused!")

        sessions[guild].pause_resume()
    else:
        await interaction.response.send_message("Not in a voice channel!")


@bot.tree.command()
async def resume(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await interaction.response.send_message("Resumed!")

        sessions[guild].pause_resume()
    else:
        await interaction.response.send_message("Not in a voice channel!")


@bot.tree.command()
async def queue(interaction: discord.Interaction):
    guild = interaction.guild
    
    if guild in sessions:
        song_queue = sessions[guild].get_song_queue()

        if len(song_queue) > 10:
            msg = "Next 10 song in queue:"

            for i in range(10):
                msg += "\n" + str(i + 1) + ". " + song_queue[i]["title"]
        else:
            msg = "Queue:"

            for i in range(len(song_queue)):
                msg += "\n" + str(i + 1) + ". " + song_queue[i]["title"]

        await interaction.response.send_message(msg)
    else:
        await interaction.response.send_message("No songs queued!")


@bot.tree.command()
async def say(interaction: discord.Interaction, msg: str):
    await interaction.response.send_message(msg)
