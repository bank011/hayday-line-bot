import os
import requests
from bs4 import BeautifulSoup

ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GROUP_ID = os.getenv("LINE_GROUP_ID")

URL = "https://hayday.com/en/news"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers, timeout=20)
r.raise_for_status()

soup = BeautifulSoup(r.text, "lxml")

title = None
link = None

for a in soup.find_all("a", href=True):
    href = a["href"]

    if "/en/news/" in href or "/news/" in href:
        text = a.get_text(strip=True)

        if len(text) > 5:
            title = text

            if href.startswith("/"):
                link = "https://hayday.com" + href
            else:
                link = href
            break
if not title:
    raise Exception("News not found")

message = {
    "to": GROUP_ID,
    "messages": [
        {
            "type": "text",
            "text": f"""📰 Hay Day News

{title}

{link}"""
        }
    ]
}

requests.post(
    "https://api.line.me/v2/bot/message/push",
    headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    },
    json=message,
).raise_for_status()

print("Done")
