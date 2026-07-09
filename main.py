from supercell import get_news_list
from reader import read_article
from ai import summarize
from line import send_message
from state import is_duplicate, mark_sent


def main():

    print("=" * 60)
    print("🌾 Hay Day AI News Bot")
    print("=" * 60)

    news_list = get_news_list()

    if not news_list:
        print("❌ No news found.")
        return

    sent = 0

    for news in news_list:

        print(f"\n📰 {news['title']}")

        # เช็กข่าวซ้ำ
        if is_duplicate(news["id"]):
            print("⏩ Already sent")
            continue

        # อ่านบทความ
        article = read_article(news["url"])

        if not article:
            print("❌ Article not found")
            continue

        if len(article["content"]) < 50:
            print("❌ Empty content")
            continue

        print("🤖 AI is summarizing...")

        result = summarize(article)

        if not result:
            print("❌ AI returned nothing")
            continue

        if result.strip().upper() == "SKIP":
            print("⏩ AI skipped")
            continue

        print("📤 Sending to LINE...")

        send_message(result)

        # บันทึกว่าข่าวนี้ส่งแล้ว
        mark_sent(news["id"])

        sent += 1

    print()
    print("=" * 60)
    print(f"✅ Finished ({sent} news sent)")
    print("=" * 60)


if __name__ == "__main__":
    main()
