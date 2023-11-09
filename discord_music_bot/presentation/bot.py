import discord


class Bot(discord.Client):
    def __init__(self, i, chat_service):
        super().__init__(intents=i)
        self.tree = discord.app_commands.CommandTree(self)
        self.chat_service = chat_service

    async def on_ready(self):
        print(str(self.user) + " connected!")
        
        await self.tree.sync()

    async def on_message(self, message):
        mention = "<@" + str(self.user.id) + ">"
        name = self.user.name

        if mention in message.content or message.reference \
                and (await message.channel.fetch_message(message.reference.message_id)).author.id == self.user.id:
            question = message.content.replace(mention, name)

            await message.reply(await self.chat_service.answer(message.channel, question, message.author, message.channel.guild))
