import discord
import typing

def initMusicCommands(bot, spotify, music_service):
    @bot.tree.command()
    async def play(
            interaction: discord.Interaction, song: str, pos: typing.Optional[int]
    ):
        await interaction.response.send_message(
            await music_service.enqueue_song(
                song, pos, interaction.user, interaction.guild, 
                interaction.channel))


    @bot.tree.command()
    async def play_file(
            interaction: discord.Interaction, file: discord.Attachment):
        await interaction.response.send_message(
            await music_service.enqueue_song(
                file, 0, interaction.user, interaction.guild, 
                interaction.channel))


    @bot.tree.command()
    async def shuffle(interaction: discord.Interaction, song: str):
        await interaction.response.send_message(
            await music_service.enqueue_song(
                song, 0, interaction.user, interaction.guild, 
                interaction.channel, shuffle=True))


    @bot.tree.command()
    async def skip(interaction: discord.Interaction):
        await interaction.response.send_message(await music_service.skip_song(interaction.guild))


    @bot.tree.command()
    async def leave(interaction: discord.Interaction):
        await interaction.response.send_message(await music_service.leave(interaction.guild))


    @bot.tree.command()
    async def pause(interaction: discord.Interaction):
        await interaction.response.send_message(music_service.pause_song(interaction.guild))


    @bot.tree.command()
    async def resume(interaction: discord.Interaction):
        await interaction.response.send_message(music_service.resume_song(interaction.guild))


    @bot.tree.command()
    async def queue(interaction: discord.Interaction):
        await interaction.response.send_message(music_service.get_song_queue(interaction.guild))


    @bot.tree.command()
    async def now_playing(interaction: discord.Interaction):
        await interaction.response.send_message(music_service.get_now_playing_song(interaction.guild))
