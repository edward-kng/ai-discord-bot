import os
from discord_music_bot.commands import *
from discord_music_bot.downloaders.spotify import Spotify

def main():
    try:
        from dotenv import load_dotenv
        
        load_dotenv()
    except ImportError:
        # python-dotenv is not installed, ignore
        pass

    try:
        import spotipy

        SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
        SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
        Spotify.spotify_client = spotipy.Spotify(
            client_credentials_manager
            = spotipy.oauth2.SpotifyClientCredentials(
                client_id = SPOTIPY_CLIENT_ID,
                client_secret = SPOTIPY_CLIENT_SECRET))
    except ImportError:
        # spotipy is not installed, ignore
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