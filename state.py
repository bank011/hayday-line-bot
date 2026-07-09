import json
import os

from config import STATE_FILE


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            state,
            f,
            ensure_ascii=False,
            indent=4
        )


def is_duplicate(source, news_id):

    state = load_state()

    if state.get(source) == news_id:
        return True

    state[source] = news_id

    save_state(state)

    return False
