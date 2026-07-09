import os
import feedparser
import requests

CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
GROUP_ID = os.environ["LINE_GROUP_ID"]

RSS = "https://supercell.com/en/rss/"

feed = feedparser.parse(RSS)

hayday = None

for entry in feed.entries:
    title = entry.title.lower()

    if "hay day" in title:
        hayday = entry
        break

if hayday is None:
    print("No Hay Day news.")
    exit(0)

message = {
    "to": GROUP_ID,
    "messages": [
        {
            "type": "text",
            "text": f"""🎮 Hay Day News

{hayday.title}

{hayday.link}
"""
        }
    ]
}

headers = {
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

res = requests.post(
    "https://api.line.me/v2/bot/message/push",
    headers=headers,
    json=message
)

print(res.status_code)
print(res.text)
