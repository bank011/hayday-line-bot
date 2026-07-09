from supercell import get_news_list
from reader import read_article
from ai import summarize
from line import send_message
from state import is_duplicate


def main():

    print("=" * 60)
    print("Hay Day AI News Bot")
    print("=" * 60)

    news_list = get_news_list()

    if not news_list:
        print("No news found.")
        return

    sent = 0

    for news in news_list:

        print(f"\nChecking : {news['title']}")

        if is_duplicate("supercell", news["id"]):
            print("Already sent.")
            continue

        article = read_article(news["url"])

        if not article["content"]:
            print("Article empty.")
            continue

        result = summarize(article)

        if result.strip().upper() == "SKIP":
            print("AI skipped.")
            continue

        send_message(result)

        sent += 1

    print(f"\nFinished ({sent} news sent)")


if __name__ == "__main__":
    main()
