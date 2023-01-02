import yt_dlp

class YouTubeGeneric:
    def get_metadata(query):
        track_list = []

        if "youtube.com" in query:

            ytdl = yt_dlp.YoutubeDL()

            try:
                metadata = ytdl.extract_info(
                    query, download = False, process = False)
            except:
                return None

            if "entries" in metadata:
                for entry in metadata["entries"]:
                    track_list.append({
                        "query": entry["url"], "id": "youtube_" + entry["id"],
                        "title": entry["title"],
                        "type": "song_youtube_generic"})
            else:
                track_list.append({
                        "query": query, "id": "youtube_" + metadata["id"],
                        "title": metadata["title"],
                        "type": "song_youtube_generic"})
        
        # Query is not a YouTube URL, use search or generic downloader
        else:
            ytdl = yt_dlp.YoutubeDL({"default_search": "ytsearch"})

            try:
                metadata = ytdl.extract_info(query, download = False)

            except:
                return None

            result = metadata["entries"][0]
            track_list.append({
                        "query": query, "id": "generic_" + result["id"],
                        "title": result["title"],
                        "type": "song_youtube_generic"})

        return track_list

    def download(song, location):
        ytdl = yt_dlp.YoutubeDL({
            "format": "bestaudio", "outtmpl": location,
            "default_search": "ytsearch", "noplaylist": True})

        ytdl.download(song["query"])
