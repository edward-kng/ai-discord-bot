from dataclasses import dataclass
from typing import Union

@dataclass
class Song:
    query: str
    audio: str
    title: str
    type: str
    track_title: str = None