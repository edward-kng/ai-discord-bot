import json
import os
import shutil
from threading import Thread

import discord
import requests


TMP_DIR = "tmp/"


def download(attachment: discord.Attachment, path: str) -> None:
    response = requests.get(attachment.url)

    with open(str(path) + "/files/" + attachment.filename, "wb") as file:
        file.write(response.content)


async def export_history(channel: discord.TextChannel) -> None:
    path = TMP_DIR + str(channel.id)

    if not os.path.exists(path + "/files"):
        os.makedirs(path + "/files")

    history = await download_history(channel)

    with open(path + "/history.json", "w") as history_file:
        json.dump(history, history_file)

    shutil.make_archive(path, "zip", path)

    zip_path = path + ".zip"

    await channel.send("Chat history export finished!", file=discord.File(zip_path))

    shutil.rmtree(path)
    os.remove(zip_path)


async def download_history(
    channel: discord.TextChannel, limit: int | None = None, download_images=True
) -> dict:
    path = TMP_DIR + str(channel.id)
    history = {"messages": []}
    threads = []

    async for message in channel.history(limit=limit):
        history["messages"].append(
            parse_message(message, threads, path, download_images)
        )

    for thread in threads:
        thread.join()

    return history


def parse_message(
    message: discord.Message, threads: list[Thread], path: str, download_images=False
):
    data = {
        "sender": {
            "name": message.author.name,
            "id": message.author.id,
        },
        "sent": str(message.created_at),
        "messageContent": message.content,
    }

    if message.edited_at is not None:
        data["edited"] = str(message.edited_at)

    if len(message.attachments) > 0:
        data["files"] = []

    for attachment in message.attachments:
        file_data = {"fileName": attachment.filename, "url": attachment.url}

        data["files"].append(file_data)

        if download_images:
            thread = Thread(target=download, args=(attachment, path))
            threads.append(thread)
            thread.start()

    return data
