import yt_dlp

class Spotify:
    spotify_client = None

    def get_metadata(url):
        track_list = []

        if Spotify.spotify_client is None:
                return None
        
        if "playlist" in url:
            playlist = Spotify.spotify_client.playlist_tracks(url)
            
            for track in playlist["items"]:
                track_list.append(
                    Spotify._get_track_metadata(track["track"]))
        elif "album" in url:
            album = Spotify.spotify_client.album_tracks(url)

            for track in album["items"]:
                track_list.append(
                    Spotify._get_track_metadata(track))
        else:
            track = Spotify.spotify_client.track(url)

            track_list.append(Spotify._get_track_metadata(track))

        return track_list

    def _get_track_metadata(track):
        metadata = {
            "query": track["artists"][0]["name"],
            "title": track["artists"][0]["name"]}

        for i in range(1, len(track["artists"])):
            metadata["title"] += ", " + track["artists"][i]["name"]
            metadata["query"] += " " + track["artists"][i]["name"]

        metadata["title"] += " - " + track["name"]

        # Add 'audio' to query to avoid downloading music videos
        metadata["query"] += " " + track["name"] + " audio"

        metadata["type"] = "song_spotify"
        metadata["id"] = "spotify_" + track["id"]
        metadata["track_title"] = track["name"]

        return metadata

    def download(song, location):
        ytdl = yt_dlp.YoutubeDL({
            "format": "bestaudio", "outtmpl": location,
            "default_search": "ytsearch", "noplaylist": True})

        metadata = ytdl.extract_info(song["query"], download = False)

        """
        For some reason, YouTube search sometimes returns completely
        irrelevant videos when searching for less known songs and the word
        'audio' is added. To mitigate this, we check whether the
        title resembles the Spotify title, and if not, we download again,
        without searching for 'audio'.
        """

        if song["track_title"].lower() not in metadata[
            "entries"][0]["title"].lower():
            ytdl.download(song["query"].replace(" audio", ""))
        else:
            ytdl.download(song["query"])
