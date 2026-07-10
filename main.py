from supercell import get_latest_news
from reader import read_article
from ai import summarize
from line import send_message
from state import is_duplicate, mark_sent


def main():

    print("=" * 60)
    print("🌾 Hay Day AI News Bot")
    print("=" * 60)

    news = get_latest_news()

    if news is None:
        print("No Hay Day news found.")
        return

    print(f"Latest News : {news['title']}")

    # ข่าวนี้เคยส่งแล้วหรือยัง
    if is_duplicate(news["id"]):
        print("Already sent.")
        return

    print("Reading article...")

    article = read_article(news["url"])

    if not article:
        print("Article not found.")
        return

    if len(article["content"]) < 50:
        print("Article content empty.")
        return

    print("AI Summarizing...")

    result = summarize(article)

    if not result:
        print("AI returned nothing.")
        return

    if result.strip().upper() == "SKIP":
        print("AI skipped this news.")
        mark_sent(news["id"])
        return

    print("Sending LINE...")

    send_message(result)

    # จำว่าข่าวนี้ส่งแล้ว
    mark_sent(news["id"])

    print("Done.")


if __name__ == "__main__":
    main()
