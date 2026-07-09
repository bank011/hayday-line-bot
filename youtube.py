import feedparser

RSS = "https://www.youtube.com/@hayday"


def get_latest():

    feed = feedparser.parse(RSS)

    if not feed.entries:
        return None

    item = feed.entries[0]

    return {
        "id": item.id,
        "title": item.title,
        "link": item.link,
        "source": "YouTube"
    }
