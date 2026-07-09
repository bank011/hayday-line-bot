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

    # ลบ tag ที่ไม่ต้องการ
    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "header",
        "footer",
        "nav"
    ]):
        tag.decompose()

    paragraphs = []

    for p in soup.find_all("p"):

        text = p.get_text(" ", strip=True)

        if len(text) < 30:
            continue

        paragraphs.append(text)

    article = "\n\n".join(paragraphs)

    return article
