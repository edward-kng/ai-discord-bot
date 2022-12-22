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

    try:
        clear_cache("cache")
    except FileNotFoundError:
        os.mkdir("cache")
    
    bot.run(TOKEN)

def clear_cache(path):
    for file in os.listdir(path):
        file_path = path + "/" + file

        if os.path.isdir(file_path):
            try:
                os.rmdir(file_path)
            except OSError:
                clear_cache(file_path)
        else:
            os.remove(file_path)

if __name__ == "__main__":
    main()
