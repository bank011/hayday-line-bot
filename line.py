import os
import requests

TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
GROUP = os.environ["LINE_GROUP_ID"]


def send(text):

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "to": GROUP,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=body
    )

    print(r.status_code)
    print(r.text)
