import requests
from bs4 import BeautifulSoup

URL = "https://supercell.com/en/news/"


def get_latest_news():

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

    articles = []

    for a in soup.find_all("a", href=True):

        href = a.get("href", "")

        if "/news/" not in href:
            continue

        if href.startswith("/"):
            href = "https://supercell.com" + href

        title = a.get_text(" ", strip=True)

        if len(title) < 10:
            continue

        check = (title + href).lower()

        if "hay day" not in check:
            continue

        articles.append({
            "id": href,
            "title": title,
            "url": href
        })

    # เอาเฉพาะข่าวล่าสุด
    if articles:
        return articles[0]

    return None
