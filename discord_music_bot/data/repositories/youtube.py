from yt_dlp import YoutubeDL


class YouTubeRepository:
    def __init__(self) -> None:
        self._yt_client = YoutubeDL()
        self._generic_client = YoutubeDL(
            {"format": "best", "default_search": "ytsearch"}
        )
        self._audio_client = YoutubeDL(
            {"format": "best", "default_search": "ytsearch", "noplaylist": True}
        )

    def get_metadata_yt_url(self, url: str) -> dict:
        return self._yt_client.extract_info(url, download=False, process=False)

    def get_metadata_generic(self, query: str) -> dict:
        return self._generic_client.extract_info(query, download=False)

    def get_audio_stream(self, query: str) -> str:
        return self._audio_client.extract_info(query, download=False)["url"]
