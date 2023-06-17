import os
from discord_music_bot.di.app_container import AppContainer

app_container = AppContainer()

from discord_music_bot.commands import *


def main():
    try:
        from dotenv import load_dotenv
        
        load_dotenv()
    except ImportError:
        # python-dotenv is not installed, ignore
        pass

    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    app_container.bot.run(TOKEN)


if __name__ == "__main__":
    main()
