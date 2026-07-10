import feedparser

CHANNEL_ID = "UC27cEfYbMEA006oOOKc9hKA"

RSS = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"


def get_latest_video():

    feed = feedparser.parse(RSS)

    if not feed.entries:
        return None

    item = feed.entries[0]

    return {
        "id": item.yt_videoid,
        "title": item.title,
        "link": item.link,
        "published": item.published,
        "summary": item.summary
    }
