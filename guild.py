from asyncio import Condition, Lock

class Guild:
    def __init__(self):
        self.play_queue = []
        self.download_queue = []
        self.downloaded_songs = []
        self.skipped = False
        self.paused = False
        self.active = True
        self.lock = Lock()
        self.download_ready = Condition()
        self.song_ready = Condition()
        self.download_task = None
        self.playback_task = None
