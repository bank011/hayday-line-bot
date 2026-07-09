import requests

from config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_GROUP_ID,
)


def send_message(text: str):

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "to": LINE_GROUP_ID,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=payload,
        timeout=30,
    )

    print("Status :", r.status_code)
    print("Response :", r.text)

    r.raise_for_status()
