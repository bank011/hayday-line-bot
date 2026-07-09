import feedparser

from state import is_duplicate

RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UC27cEfYbMEA006oOOKc9hKA"


def get_news():

    feed = feedparser.parse(RSS)

    if not feed.entries:
        return None

    item = feed.entries[0]

    news = {
        "source": "YouTube",
        "id": item.id,
        "title": item.title,
        "link": item.link
    }

    if is_duplicate("youtube", news["id"]):
        return None

    return news
