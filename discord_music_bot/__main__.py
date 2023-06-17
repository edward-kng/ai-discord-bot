import os
import openai
from .di.app_container import AppContainer

app_container = AppContainer()

from .presentation.commands.music import *
from .presentation.commands.chat import *


def main():
    try:
        from dotenv import load_dotenv
        
        load_dotenv()
    except ImportError:
        # python-dotenv is not installed, ignore
        pass

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY

    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    app_container.bot.run(TOKEN)


if __name__ == "__main__":
    main()
