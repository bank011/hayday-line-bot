import feedparser

def get_latest_fb_post():
    # เปลี่ยนเป็น URL RSS ของเพจ Facebook ที่คุณไปแปลงมา
    rss_url = "https://fetchrss.com/rss/your_facebook_page_feed" 
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        return None
        
    latest_entry = feed.entries[0]
    return {
        "id": latest_entry.id,
        "text": latest_entry.summary, # ข้อความในโพสต์
        "link": latest_entry.link
    }
