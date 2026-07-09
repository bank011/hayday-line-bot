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
        print("No Hay Day news found.")
        return

    sent = 0

    for news in news_list:

        print(f"Checking : {news['title']}")

        if is_duplicate(news["id"]):
            print("Already sent")
            continue

        article = read_article(news["url"])

        if not article["content"]:
            print("Empty article")
            continue

        result = summarize(article)

        if not result:
            print("AI Error")
            continue

        if result.strip().upper() == "SKIP":
            print("Skip")
            continue

        send_message(result)

        mark_sent(news["id"])

        sent += 1

    print(f"Finished ({sent} news sent)")


if __name__ == "__main__":
    main()
