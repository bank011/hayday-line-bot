from youtube import get_latest_video
from ai import summarize
from line import send_message
from state import is_sent, mark


def main():

    print("Hay Day Home Bot")

    video = get_latest_video()

    if video is None:
        print("No video")
        return

    if is_sent(video["id"]):
        print("Already sent")
        return

    result = summarize(video)

    if result.strip().upper() == "SKIP":
        mark(video["id"])
        print("Skip")
        return

    message = f"""{result}

━━━━━━━━━━━━━━━━━━

🔗 ต้นฉบับ

{video["link"]}
"""

    send_message(message)

    mark(video["id"])

    print("Done")


if __name__ == "__main__":
    main()
