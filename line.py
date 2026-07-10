import requests

from config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_GROUP_ID
)


def send_message(text):

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "to": LINE_GROUP_ID,
        "messages": [
            {
                "type": "text",
                "text": text[:4900]
            }
        ]
    }

    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=body,
        timeout=30
    )

    r.raise_for_status()
