import yt_dlp
import spotipy


def get_audio(song: dict):
    ytdl = yt_dlp.YoutubeDL(
        {"format": "bestaudio", "default_search": "ytsearch", "noplaylist": True}
    )

    metadata = ytdl.extract_info(song["query"], download=False)

    """
    For some reason, YouTube search sometimes returns completely
    irrelevant videos when searching for less known songs and the word
    'audio' is added. To mitigate this, we check whether the
    title resembles the Spotify title, and if not, we download again,
    without searching for 'audio'.
    """

    if (
        len(metadata["entries"]) == 0
        or song["track_title"].lower() not in metadata["entries"][0]["title"].lower()
    ):
        metadata = ytdl.extract_info(
            song["query"].replace(" audio", ""), download=False
        )

    if len(metadata["entries"]) > 0:
        return metadata["entries"][0]["url"]

    return None


def _get_track_metadata(track: dict):
    metadata = {
        "query": track["artists"][0]["name"],
        "title": track["artists"][0]["name"],
    }

    for i in range(1, len(track["artists"])):
        metadata["title"] += ", " + track["artists"][i]["name"]
        metadata["query"] += " " + track["artists"][i]["name"]

    metadata["title"] += " - " + track["name"]

    # Add 'audio' to query to avoid downloading music videos
    metadata["query"] += " " + track["name"] + " audio"

    metadata["type"] = "spotify"
    metadata["track_title"] = track["name"]

    return metadata


class Spotify:
    def __init__(self, spotify_client: spotipy.Spotify):
        self._spotify_client = spotify_client

    def get_metadata(self, url: str):
        track_list = []

        if self._spotify_client is None:
            return None

        if "playlist" in url:
            try:
                playlist = self._spotify_client.playlist_tracks(url)
            except:
                return None

            for track in playlist["items"]:
                track_list.append(_get_track_metadata(track["track"]))
        elif "album" in url:
            try:
                album = self._spotify_client.album_tracks(url)
            except:
                return None

            for track in album["items"]:
                track_list.append(_get_track_metadata(track))
        else:
            try:
                track = self._spotify_client.track(url)
            except:
                return None

            track_list.append(_get_track_metadata(track))

        return track_list
