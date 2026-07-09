from supercell import get_news_list
from reader import read_article
from ai import summarize
from line import send_message
from state import is_duplicate


def main():

    print("=" * 50)
    print("Hay Day AI News Bot")
    print("=" * 50)

    news_list = get_news_list()

    if len(news_list) == 0:
        print("No news.")
        return

    for news in news_list:

        print("Checking :", news["title"])

        if is_duplicate("supercell", news["id"]):
            print("Already sent.")
            continue

        article = read_article(news["url"])

        if len(article["content"]) < 50:
            print("Empty article.")
            continue

        result = summarize(article)

        if result.strip().upper() == "SKIP":
            print("Skip")
            continue

        send_message(result)

        print("Sent")

    print("Done")


if __name__ == "__main__":
    main()
