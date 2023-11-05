import discord

from ...domain.history import export_history as export_history_logic

def initChatCommands(bot, chat_service):
    @bot.tree.command()
    async def say(interaction: discord.Interaction, msg: str):
        await interaction.response.send_message(msg)


    @bot.tree.command()
    async def export_history(interaction: discord.Interaction):
        await interaction.response.send_message("Exporting chat history...")
        await export_history_logic(interaction.channel)


    @bot.tree.command()
    async def memory(interaction: discord.Interaction, nr: int):
        chat_service.memory = nr

        await interaction.response.send_message("Memory set to " + str(nr) + " messages!")
