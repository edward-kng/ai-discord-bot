from discord_music_bot.logic.utils.music.song import Song
import yt_dlp
from spotipy import Spotify

from discord_music_bot.data.repositories.youtube import YouTubeRepository


def _get_track_metadata(track: dict) -> Song:
    metadata = {
        "query": track["artists"][0]["name"],
        "title": track["artists"][0]["name"],
    }
    metadata = Song(track["artists"][0]["name"], None, track["artists"][0]["name"], "spotify", track["name"])

    for i in range(1, len(track["artists"])):
        metadata.title += ", " + track["artists"][i]["name"]
        metadata.query += " " + track["artists"][i]["name"]

    metadata.title += " - " + track["name"]

    # Add 'audio' to query to avoid downloading music videos
    metadata.query += " " + track["name"] + " audio"

    return metadata


class MusicFetcher:
    def __init__(
        self, youtube_repository: YouTubeRepository, spotify_client: Spotify
    ) -> None:
        self._youtube_repository = youtube_repository
        self._spotify_client = spotify_client

    def get_metadata(self, query: str) -> list[Song] | None:
        track_list = []

        if "youtube.com" in query:
            try:
                metadata = self._youtube_repository.get_metadata_yt_url(query)
            except:
                return None

            if "entries" in metadata:
                for entry in metadata["entries"]:
                    track_list.append(Song(entry["url"], None, entry["title"], "youtube_generic"))
            else:
                track_list.append(Song(query, None, metadata["title"], "youtube_generic"))
        elif "spotify.com" in query:
            track_list = []

            if self._spotify_client is None:
                return None

            if "playlist" in query:
                try:
                    playlist = self._spotify_client.playlist_tracks(query)
                except:
                    return None

                for track in playlist["items"]:
                    track_list.append(_get_track_metadata(track["track"]))
            elif "album" in query:
                try:
                    album = self._spotify_client.album_tracks(query)
                except:
                    return None

                for track in album["items"]:
                    track_list.append(_get_track_metadata(track))
            else:
                try:
                    track = self._spotify_client.track(query)
                except:
                    return None

                track_list.append(_get_track_metadata(track))

            return track_list

        # Query is not a YouTube URL, use search or generic downloader
        else:
            try:
                metadata = self._youtube_repository.get_metadata_generic(query)
            except:
                return None

            if "entries" in metadata:
                metadata = metadata["entries"][0]

            track_list.append(Song(query, metadata["url"], metadata["title"], "youtube_generic"))

        return track_list

    def get_audio(self, song: Song) -> str | None:
        if song.type == "spotify":
            ytdl = yt_dlp.YoutubeDL(
                {
                    "format": "bestaudio",
                    "default_search": "ytsearch",
                    "noplaylist": True,
                }
            )

            metadata = ytdl.extract_info(song.query, download=False)

            """
            For some reason, YouTube search sometimes returns completely
            irrelevant videos when searching for less known songs and the word
            'audio' is added. To mitigate this, we check whether the
            title resembles the Spotify title, and if not, we download again,
            without searching for 'audio'.
            """

            if (
                len(metadata["entries"]) == 0
                or song.track_title.lower()
                not in metadata["entries"][0]["title"].lower()
            ):
                metadata = ytdl.extract_info(
                    song.query.replace(" audio", ""), download=False
                )

            if len(metadata["entries"]) > 0:
                return metadata["entries"][0]["url"]

            return None

        return self._youtube_repository.get_audio_stream((song.query))
