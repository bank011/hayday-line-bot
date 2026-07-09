import os
import requests

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_GROUP_ID = os.environ["LINE_GROUP_ID"]

def send_line_message(text: str) -> None:
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": LINE_GROUP_ID,
        "messages": [
            {"type": "text", "text": text}
        ],
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    print("Sent:", r.status_code, r.text)

if __name__ == "__main__":
    send_line_message("🎉 Hay Day News Bot พร้อมใช้งานแล้ว!")
