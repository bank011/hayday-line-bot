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

    paragraphs = []

    for p in soup.find_all("p"):

        text = p.get_text(
            " ",
            strip=True
        )

        if len(text) < 20:
            continue

        paragraphs.append(text)

    return {
        "title": soup.title.text if soup.title else "",
        "date": "",
        "content": "\n\n".join(paragraphs)
    }
