import feedparser

RSS = "https://supercell.com/en/rss/"


def get_latest():

    feed = feedparser.parse(RSS)

    if not feed.entries:
        return None

    for item in feed.entries:

        title = item.title.lower()

        if "hay day" in title:
            return {
                "id": item.id,
                "title": item.title,
                "link": item.link,
                "source": "Supercell"
            }

    return None
