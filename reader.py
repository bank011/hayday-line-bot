import requests
from bs4 import BeautifulSoup


def read_article(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # ลบ script และ style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = []

    # ดึงข้อความจาก paragraph
    for p in soup.find_all("p"):

        t = p.get_text(" ", strip=True)

        if len(t) < 20:
            continue

        text.append(t)

    article = "\n\n".join(text)

    return article
