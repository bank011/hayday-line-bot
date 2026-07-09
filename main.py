from youtube import get_news
from line import send_message
from ai import summarize


def main():

    news = get_news()

    if news is None:
        print("No new news.")
        return

    text = f"""
Title:
{news['title']}

Description:
{news['description']}
"""

    result = summarize(text)

    send_message(result)

    print("Done")


if __name__ == "__main__":
    main()
