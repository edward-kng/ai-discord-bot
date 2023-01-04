import discord


class Bot(discord.Client):
    def __init__(self, i):
        super().__init__(intents=i)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        print(str(self.user) + " connected!")
        
        await self.tree.sync()
