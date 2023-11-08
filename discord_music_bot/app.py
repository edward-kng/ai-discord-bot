import os

import discord
import openai
import spotipy
from dotenv import load_dotenv
from .presentation.bot import Bot
from .domain.spotify import Spotify
from .domain.services.music import MusicService
from discord_music_bot.domain.services.chat import ChatService
from .presentation.commands.music import initMusicCommands
from .presentation.commands.chat import initChatCommands


class App:
    def __init__(self):
        load_dotenv()

        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = Bot(intents, None)
        spotify = None

        SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
        SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
        spotify_client = spotipy.Spotify(
            client_credentials_manager
            =spotipy.oauth2.SpotifyClientCredentials(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET))

        spotify = Spotify(spotify_client)

        chat_service = ChatService(self.bot)
        self.bot.chat_service = chat_service
        initMusicCommands(self.bot, spotify, MusicService(self.bot, spotify))
        initChatCommands(self.bot, chat_service)

        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def run(self):
        self.bot.run(os.getenv('DISCORD_BOT_TOKEN'))
