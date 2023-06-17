import discord

from discord_music_bot.openai import answer


class Bot(discord.Client):
    def __init__(self, i):
        super().__init__(intents=i)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        print(str(self.user) + " connected!")
        
        await self.tree.sync()

    async def on_message(self, message):
        mention = "<@" + str(self.user.id) + ">"
        name = self.user.name

        if mention in message.content:
            question = message.content.replace(mention, name)
            await message.channel.send(await answer(question, name))
