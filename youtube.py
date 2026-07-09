import feedparser

RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UC4P6A5l4j4J6LQx5q3gY0Ag"


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
