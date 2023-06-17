import json
import os
import requests
from threading import Thread


def download(attachment, path):
    response = requests.get(attachment.url)

    with open(str(path) + "/files/" + attachment.filename, "wb") as file:
        file.write(response.content)


async def export_history(feedback_channel):
    history = {"messages": []}
    threads = []
    path = "chat-history/" + str(feedback_channel.id)

    if not os.path.exists(path + "/files"):
        os.makedirs(path + "/files")

    async for message in feedback_channel.history(limit=None):
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

            thread = Thread(target=download, args=(attachment, path))
            threads.append(thread)
            thread.start()

        history["messages"].append(data)

    with open(path + "/history.json", "w") as history_file:
        json.dump(history, history_file)

    for thread in threads:
        thread.join()

    await feedback_channel.send("Chat history export finished!")
