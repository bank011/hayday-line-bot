import json
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

    result = {
        "title": "",
        "date": "",
        "content": "",
        "image": ""
    }

    # ----------------------------
    # JSON-LD
    # ----------------------------

    for tag in soup.find_all("script", type="application/ld+json"):

        try:

            data = json.loads(tag.string)

            if isinstance(data, dict):

                result["title"] = data.get("headline", "")

                result["date"] = data.get("datePublished", "")

                result["image"] = data.get("image", "")

        except Exception:
            pass

    # ----------------------------
    # เนื้อหา
    # ----------------------------

    paragraphs = []

    for p in soup.find_all("p"):

        text = p.get_text(" ", strip=True)

        if len(text) < 30:
            continue

        paragraphs.append(text)

    result["content"] = "\n\n".join(paragraphs)

    return result
