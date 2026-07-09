from line import send_message
from supercell import get_news
from reader import read_article
from ai import summarize
from state import is_duplicate


def main():

    print("================================")
    print(" Hay Day AI News Bot")
    print("================================")

    news = get_news()

    if news is None:
        print("No news found.")
        return

    print(f"Found : {news['title']}")

    if is_duplicate("supercell", news["url"]):
        print("Already sent.")
        return

    print("Reading article...")

    article = read_article(news["url"])

    if not article:
        print("Article is empty.")
        return

    print("Summarizing with Groq...")

    result = summarize(article)

    if not result:
        print("No AI response.")
        return

    if result.strip().upper() == "SKIP":
        print("Skip this article.")
        return

    print("Sending LINE...")

    send_message(result)

    print("Done.")


if __name__ == "__main__":
    main()
