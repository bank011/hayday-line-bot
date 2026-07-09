import requests
from bs4 import BeautifulSoup

URL = "https://supercell.com/en/news/announcement/hayday/page/1/"


def get_news():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    articles = []

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "/news/" not in href:
            continue

        if href.startswith("/"):
            href = "https://supercell.com" + href

        title = a.get_text(" ", strip=True)

        if len(title) < 8:
            continue

        articles.append({
            "title": title,
            "url": href
        })

    # ลบข่าวซ้ำ
    unique = []

    seen = set()

    for item in articles:

        if item["url"] in seen:
            continue

        seen.add(item["url"])

        unique.append(item)

    if len(unique) == 0:
        return None

    return unique[0]
