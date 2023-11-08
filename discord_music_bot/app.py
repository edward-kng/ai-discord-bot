import os

import discord
from dotenv import load_dotenv
from .presentation.bot import Bot
from .domain.spotify import Spotify
from .domain.services.music import MusicService
from discord_music_bot.domain.services.chat import ChatService
from .presentation.commands.music import initMusicCommands
from .presentation.commands.chat import initChatCommands
from openai import OpenAI


class App:
    def __init__(self):
        try:
            from dotenv import load_dotenv
        
            load_dotenv()
        except ImportError:
            # python-dotenv is not installed, ignore
            pass

        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = Bot(intents, None)
        spotify = None

        try:
            import spotipy

            SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
            SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
            spotify_client = spotipy.Spotify(
                client_credentials_manager
                =spotipy.oauth2.SpotifyClientCredentials(
                    client_id=SPOTIPY_CLIENT_ID,
                    client_secret=SPOTIPY_CLIENT_SECRET))

            spotify = Spotify(spotify_client)
        except ImportError:
            # spotipy is not installed, ignore
            pass

        OPENAI_KEY = os.getenv("OPENAI_API_KEY")

        if OPENAI_KEY:
            openai_client = OpenAI(api_key = OPENAI_KEY)
        else:
            openai_client = None

        music_service = MusicService(self.bot, spotify)
        chat_service = ChatService(self.bot, openai_client, music_service)
        self.bot.chat_service = chat_service
        initMusicCommands(self.bot, spotify, music_service)
        initChatCommands(self.bot, chat_service)
    
    def run(self):
        self.bot.run(os.getenv('DISCORD_BOT_TOKEN'))
