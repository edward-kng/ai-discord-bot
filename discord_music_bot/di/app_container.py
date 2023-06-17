import discord

from discord_music_bot.bot import Bot
from discord_music_bot.downloaders.spotify import Spotify


class AppContainer:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = Bot(intents)
        self.spotify = None

        try:
            import spotipy

            SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
            SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
            spotify_client = spotipy.Spotify(
                client_credentials_manager
                =spotipy.oauth2.SpotifyClientCredentials(
                    client_id=SPOTIPY_CLIENT_ID,
                    client_secret=SPOTIPY_CLIENT_SECRET))

            self.spotify = Spotify(spotify_client)
        except ImportError:
            # spotipy is not installed, ignore
            pass