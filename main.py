from youtube import get_latest as youtube_latest
from supercell import get_latest as supercell_latest

from classifier import is_important

from line import send_message

from state import load_state, save_state


def process(news):

    if news is None:
        return

    state = load_state()

    last = state.get(news["source"])

    if last == news["id"]:
        print("Duplicate")
        return

    if not is_important(news["title"]):
        print("Skip")
        return

    send_message(
        f"""🎮 {news["source"]}

{news["title"]}

{news["link"]}
"""
    )

    state[news["source"]] = news["id"]

    save_state(state)


def main():

    process(youtube_latest())

    process(supercell_latest())


if __name__ == "__main__":
    main()
