# Discord Music Bot

A Discord bot that plays music from YouTube, SoundCloud and others.

## Commands
- `/play <song URL>` - play/enqueue a song
- `/skip` - skip the current song
- `/leave` - leave the voice chat
- `/say <message>` - send a message in the chat

## Pip dependencies
- discord.py
- yt_dlp
- python-dotenv (optional)

## Setup
1. Install Python 3 and the required dependencies above.
2. Clone the repo.
2. Create an application and bot on the Discord Developer site and add it to your server.
3. Copy your bot's token from the Discord Developer site.
4. Create the `DISCORD_BOT_TOKEN` environment variable in your shell config or by creating a `.env` file containing:

```
DISCORD_BOT_TOKEN=<your token>
```

5. Execute the `run.py` file.