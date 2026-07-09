import os
import requests
from bs4 import BeautifulSoup

ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
GROUP_ID = os.environ["LINE_GROUP_ID"]

URL = "https://hayday.com/en/news"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers, timeout=20)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

title = None
link = None

for a in soup.select("a[href]"):
    href = a.get("href", "")
    text = a.get_text(" ", strip=True)

    if len(text) < 5:
        continue

    if href.startswith("/"):
        href = "https://hayday.com" + href

    if "hayday.com" in href:
        title = text
        link = href
        break

if title is None:
    title = "ไม่พบข่าวล่าสุด"
    link = "https://hayday.com/en/news"

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

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.line.me/v2/bot/message/push",
    headers=headers,
    json=message,
    timeout=20
)

print(response.status_code)
print(response.text)

response.raise_for_status()

print("ส่งข้อความสำเร็จ")
