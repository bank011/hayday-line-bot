import requests
from bs4 import BeautifulSoup

URL = "https://supercell.com/en/news/announcement/hayday/page/1/"


def get_news():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    seen = set()

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "/news/" not in href:
            continue

        if href.startswith("/"):
            href = "https://supercell.com" + href

        if href in seen:
            continue

        seen.add(href)

        title = a.get_text(" ", strip=True)

        if len(title) < 8:
            continue

        return {
            "id": href,
            "title": title,
            "url": href,
            "source": "Supercell"
        }

    return None
