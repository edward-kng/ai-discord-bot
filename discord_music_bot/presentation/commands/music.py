import typing

import discord
from ...logic.services.music import MusicService


def init_music_commands(bot, music_service: MusicService) -> None:
    @bot.tree.command()
    async def play(
        interaction: discord.Interaction, song: str, pos: typing.Optional[int]
    ) -> None:
        await interaction.response.send_message(
            await music_service.enqueue_song(
                song, pos, interaction.user, interaction.guild, interaction.channel
            )
        )

    @bot.tree.command()
    async def play_next(
        interaction: discord.Interaction, song: str, pos: typing.Optional[int]
    ) -> None:
        await interaction.response.send_message(
            await music_service.enqueue_song(
                song,
                pos,
                interaction.user,
                interaction.guild,
                interaction.channel,
                play_next=True,
            )
        )

    @bot.tree.command()
    async def play_file(
        interaction: discord.Interaction, file: discord.Attachment
    ) -> None:
        await interaction.response.send_message(
            await music_service.enqueue_song(
                file, 0, interaction.user, interaction.guild, interaction.channel
            )
        )

    @bot.tree.command()
    async def play_file_next(
        interaction: discord.Interaction, file: discord.Attachment
    ) -> None:
        await interaction.response.send_message(
            await music_service.enqueue_song(
                file,
                0,
                interaction.user,
                interaction.guild,
                interaction.channel,
                play_next=True,
            )
        )

    @bot.tree.command()
    async def shuffle(interaction: discord.Interaction, song: str) -> None:
        await interaction.response.send_message(
            await music_service.enqueue_song(
                song,
                0,
                interaction.user,
                interaction.guild,
                interaction.channel,
                shuffle=True,
            )
        )

    @bot.tree.command()
    async def skip(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            await music_service.skip_song(interaction.guild)
        )

    @bot.tree.command()
    async def leave(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            await music_service.leave(interaction.guild)
        )

    @bot.tree.command()
    async def pause(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            music_service.pause_song(interaction.guild)
        )

    @bot.tree.command()
    async def resume(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            music_service.resume_song(interaction.guild)
        )

    @bot.tree.command()
    async def queue(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            music_service.get_song_queue(interaction.guild)
        )

    @bot.tree.command()
    async def now_playing(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            music_service.get_now_playing_song(interaction.guild)
        )
