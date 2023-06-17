import discord

from discord_music_bot.bot import Bot


class AppContainer:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = Bot(intents)
