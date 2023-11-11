# AI Discord Bot

An AI-powered Discord bot that can play music from YouTube, Spotify and 
SoundCloud, export your chat history and answer all your questions.

## Usage

To chat, simply send a message and mention the bot (with @). Reply to continue 
the conversation. The bot responds to requests in natural language, for 
example: `Play some jazz.` or `Pause the music.`. If you prefer, you can also 
use the commands below instead.

### Music

- `/play <song URL or title> [track nr to play from]` - play/enqueue a song/
playlist
- `/play_file <file>` - play/enqueue attached music file
- `/shuffle <playlist URL>` - shuffle and play/enqueue a playlist
- `/skip` - skip the current song
- `/pause` - pause current song
- `/resume` - resume current song
- `/queue` - show song queue
- `/leave` - leave the voice chat
- `/now_playing` - show current song

### Chat

- `/say <message>` - send a message in the chat
- `/export_history` - export entire chat history to a JSON file
- `/memory <nr of messages>` - set number of previous messages to remember 
(default 10)
- `/generate-image <prompt>` - generate an image

## Setup

1. Make sure you have Python 3 installed.
2. Clone the repository and `cd` into it.
3. Create a virtual environment using:

```
python3 -m venv .venv
```

4. Install the dependencies using:

```
source .venv/bin/activate && python3 -m pip install -r requirements.txt
```

5. Create an application and bot on the
 [Discord Developer](https://discord.com/developers) site and add it to your
 server.
6. Copy your bot's token from the Discord Developer site.
7. Create the `DISCORD_BOT_TOKEN` environment variable in your shell config or
 by creating a `.env` file (requires `python-dotenv`) containing:

```
DISCORD_BOT_TOKEN=<your token>
```

8. Run the bot with:

```
sh run.sh
```

### Enabling Chat Features

1. Get an OpenAI API key and top up your account at 
[OpenAI developer platform](https://platform.openai.com/).
2. Create the `OPENAI_API_KEY` environment variable:

```
OPENAI_API_KEY=<your key>
```
3. (Re)start the bot.

### Enabling Spotify Support

1. Create an application on the 
 [Spotify for Developers](https://developer.spotify.com/) site.
2. Copy your app's client ID and client secret.
3. Create the following environment variables:

```
SPOTIPY_CLIENT_ID=<your client ID>
SPOTIPY_CLIENT_SECRET=<your client secret>
```

4. (Re)start the bot.

## Notes

For technical and legal reasons, the bot does not download any songs from
 Spotify directly. Instead, the bot grabs each song's metadata using the
 Spotify Web API and downloads an equivalent audio file from YouTube.

## Licence

Discord Music Bot  
Copyright (C) 2022 - present Edward Kang

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see
[https://www.gnu.org/licenses/](https://www.gnu.org/licenses/).
