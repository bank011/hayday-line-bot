from youtube import get_news as youtube_news
from supercell import get_news as supercell_news
from line import send_message


def send(news):

    if news is None:
        return

    text = f"""🎮 {news['source']}

📰 {news['title']}

🔗 {news['link']}
"""

    send_message(news)


def main():

    print("=== Hay Day News Bot ===")

    print("Checking YouTube...")
    send(youtube_news())

    print("Checking Supercell...")
    send(supercell_news())

    print("Done")


if __name__ == "__main__":
    main()
