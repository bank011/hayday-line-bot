import requests
from bs4 import BeautifulSoup

from state import is_duplicate

URL = "https://supercell.com/en/news/"


def get_news():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    keywords = [
        "hay day",
        "hayday"
    ]

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if href.startswith("/"):
            href = "https://supercell.com" + href

        text = a.get_text(" ", strip=True)

        if len(text) < 5:
            continue

        check = (text + " " + href).lower()

        if not any(k in check for k in keywords):
            continue

        news = {
            "source": "Supercell",
            "id": href,
            "title": text,
            "link": href,
        }

        if is_duplicate("supercell", href):
            return None

        return news

    return None
