import discord
from ..bot import Bot
from discord_music_bot.logic.utils.chat.chat import (
    export_history as export_history_logic,
)
from ...logic.services.chat import ChatService


def initChatCommands(bot: Bot, chat_service: ChatService) -> None:
    @bot.tree.command()
    async def say(interaction: discord.Interaction, msg: str) -> None:
        await interaction.response.send_message(msg)

    @bot.tree.command()
    async def export_history(interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Exporting chat history...")
        await export_history_logic(interaction.channel)

    @bot.tree.command()
    async def memory(interaction: discord.Interaction, nr: int) -> None:
        chat_service.memory = nr

        await interaction.response.send_message(
            "Memory set to " + str(nr) + " messages!"
        )
