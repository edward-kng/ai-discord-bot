from ...__main__ import app_container
import discord

from ...domain.history import export_history as export_history_logic


@app_container.bot.tree.command()
async def say(interaction: discord.Interaction, msg: str):
    await interaction.response.send_message(msg)


@app_container.bot.tree.command()
async def export_history(interaction: discord.Interaction):
    await interaction.response.send_message("Exporting chat history...")
    await export_history_logic(interaction.channel)


@app_container.bot.tree.command()
async def memory(interaction: discord.Interaction, nr: int):
    app_container.chat_service.memory = nr

    await interaction.response.send_message("Memory set to " + str(nr) + " messages!")
