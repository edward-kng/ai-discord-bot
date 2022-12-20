import os
from commands import *

def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        # python-dotenv is not installed, ignore
        pass
    
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')

    clear_cache()
    bot.run(TOKEN)

def clear_cache():
    try:
        for file in os.listdir("cache"):
            os.remove("cache/" + file)
    except FileNotFoundError:
        os.mkdir("cache")

if __name__ == "__main__":
    main()
