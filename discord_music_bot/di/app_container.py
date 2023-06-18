import os

import discord
from dotenv import load_dotenv

from ..presentation.bot import Bot
from ..domain.spotify import Spotify
from discord_music_bot.domain.services.chat import ChatService


class AppContainer:
    def __init__(self):
        load_dotenv()
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = Bot(intents, None)
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

        self.chat_service = ChatService(self.bot)
        self.bot.chat_service = self.chat_service
