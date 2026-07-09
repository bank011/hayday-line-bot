import requests
from bs4 import BeautifulSoup

URL = "https://supercell.com/en/news/"


def get_news_list():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=30)

    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    news = []

    seen = set()

    for a in soup.find_all("a", href=True):

        href = a.get("href", "")

        if "/news/" not in href:
            continue

        if href.startswith("/"):
            href = "https://supercell.com" + href

        if href in seen:
            continue

        seen.add(href)

        title = a.get_text(" ", strip=True)

        if len(title) < 10:
            continue

        if "hay day" not in (
            title.lower() + href.lower()
        ):
            continue

        news.append(
            {
                "id": href,
                "title": title,
                "url": href,
            }
        )

    return news
