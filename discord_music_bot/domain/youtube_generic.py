import yt_dlp


class YouTubeGeneric:
    @staticmethod
    def get_metadata(query):
        track_list = []

        if "youtube.com" in query:
            ytdl = yt_dlp.YoutubeDL()

            try:
                metadata = ytdl.extract_info(query, download=False, process=False)
            except:
                return None

            if "entries" in metadata:
                for entry in metadata["entries"]:
                    track_list.append(
                        {
                            "query": entry["url"],
                            "title": entry["title"],
                            "type": "youtube_generic",
                        }
                    )
            else:
                track_list.append(
                    {
                        "query": query,
                        "title": metadata["title"],
                        "type": "youtube_generic",
                    }
                )

        # Query is not a YouTube URL, use search or generic downloader
        else:
            ytdl = yt_dlp.YoutubeDL({"format": "best", "default_search": "ytsearch"})

            try:
                metadata = ytdl.extract_info(query, download=False)

            except:
                return None

            if "entries" in metadata:
                metadata = metadata["entries"][0]

            track_list.append(
                {
                    "query": query,
                    "audio": metadata["url"],
                    "title": metadata["title"],
                    "type": "youtube_generic",
                }
            )

        return track_list

    @staticmethod
    def get_audio(song):
        ytdl = yt_dlp.YoutubeDL(
            {"format": "best", "default_search": "ytsearch", "noplaylist": True}
        )

        metadata = ytdl.extract_info(song["query"], download=False)

        return metadata["url"]
