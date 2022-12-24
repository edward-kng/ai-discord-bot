from asyncio import Condition, Lock

class Guild:
    spotify_client = None
    cached_songs = {}

    def __init__(self):
        self.play_queue = []
        self.download_queue = []
        self.downloaded_songs = []
        self.skipped = False
        self.paused = False
        self.active = True
        self.download_ready = Condition()
        self.song_ready = Condition()
        self.download_task = None
        self.playback_task = None
        self.idle_task = None
