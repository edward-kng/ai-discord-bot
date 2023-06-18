import asyncio
import discord
import typing

from ...__main__ import app_container
from ...domain.idle_timer import start_idle_timer
from ...domain.session import Session

sessions = {}
idle_timers = set()

@app_container.bot.tree.command()
async def play(
        interaction: discord.Interaction, song: str, pos: typing.Optional[int]
):
    user_voice = interaction.user.voice
    guild = interaction.guild

    if not user_voice and guild not in sessions:
        await interaction.response.send_message("Join a voice channel first!")
        
        return

    await interaction.response.send_message(song)

    if guild not in sessions:
        await user_voice.channel.connect()

        voice = discord.utils.get(app_container.bot.voice_clients, guild=guild)
        sessions[guild] = Session(interaction.channel, guild, voice, app_container.spotify)

        idle_timers.add(
            asyncio.create_task(start_idle_timer(sessions, guild)))

    if pos:
        await sessions[guild].enqueue(query=song, pos=pos)
    else:
        await sessions[guild].enqueue(query=song)


@app_container.bot.tree.command()
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

        voice = discord.utils.get(app_container.bot.voice_clients, guild=guild)
        sessions[guild] = Session(interaction.channel, guild, voice, app_container.spotify)

    await sessions[guild].enqueue(query=file)


@app_container.bot.tree.command()
async def shuffle(interaction: discord.Interaction, song: str):
    user_voice = interaction.user.voice
    guild = interaction.guild

    if not user_voice and guild not in sessions:
        await interaction.response.send_message("Join a voice channel first!")

        return

    await interaction.response.send_message(song)

    if guild not in sessions:
        await user_voice.channel.connect()

        voice = discord.utils.get(app_container.bot.voice_clients, guild=guild)
        sessions[guild] = Session(interaction.channel, guild, voice, app_container.spotify)

    await sessions[guild].enqueue(query=song, shuffle=True)


@app_container.bot.tree.command()
async def skip(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await sessions[guild].skip()

        await interaction.response.send_message("Skipped!")
    else:
        await interaction.response.send_message("Not in a voice channel!")


@app_container.bot.tree.command()
async def leave(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await interaction.response.send_message("Bye!")

        await sessions[guild].quit()

        sessions.pop(guild)
    else:
        await interaction.response.send_message("Not in a voice channel!")


@app_container.bot.tree.command()
async def pause(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await interaction.response.send_message("Paused!")

        sessions[guild].pause_resume()
    else:
        await interaction.response.send_message("Not in a voice channel!")


@app_container.bot.tree.command()
async def resume(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        await interaction.response.send_message("Resumed!")

        sessions[guild].pause_resume()
    else:
        await interaction.response.send_message("Not in a voice channel!")


@app_container.bot.tree.command()
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


@app_container.bot.tree.command()
async def now_playing(interaction: discord.Interaction):
    guild = interaction.guild

    if guild in sessions:
        song = sessions[guild].get_now_playing()

        if song is not None:
            await interaction.response.send_message("Now playing: " + song)
            return

    await interaction.response.send_message("No song playing!")
