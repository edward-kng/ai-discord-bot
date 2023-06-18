import json
import os
import requests
from threading import Thread


def download(attachment, path):
    response = requests.get(attachment.url)

    with open(str(path) + "/files/" + attachment.filename, "wb") as file:
        file.write(response.content)


async def export_history(channel):
    path = "chat-history/" + str(channel.id)

    if not os.path.exists(path + "/files"):
        os.makedirs(path + "/files")

    history = await download_history(channel)

    with open(path + "/history.json", "w") as history_file:
        json.dump(history, history_file)

    await channel.send("Chat history export finished!")


async def download_history(channel, limit=None, download_images=True):
    path = "chat-history/" + str(channel.id)
    history = {"messages": []}
    threads = []

    async for message in channel.history(limit=limit):
        data = {"sender": {
            "name": message.author.name,
            "id": message.author.id,
        }, "sent": str(message.created_at),
            "messageContent": message.content
        }

        if message.edited_at is not None:
            data["edited"] = str(message.edited_at)

        if len(message.attachments) > 0:
            data["files"] = []

        for attachment in message.attachments:
            file_data = {
                "fileName": attachment.filename,
                "url": attachment.url
            }

            data["files"].append(file_data)

            if download_images:
                thread = Thread(target=download, args=(attachment, path))
                threads.append(thread)
                thread.start()

        history["messages"].append(data)

    for thread in threads:
        thread.join()

    return history
