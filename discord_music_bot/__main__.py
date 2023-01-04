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
            =spotipy.oauth2.SpotifyClientCredentials(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET))
    except ImportError:
        # spotipy is not installed, ignore
        pass

    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
