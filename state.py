import json
import os

STATE_FILE = "state.json"


def load_state():

    if not os.path.exists(STATE_FILE):
        return {"sent": []}

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_state(state):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            state,
            f,
            ensure_ascii=False,
            indent=2
        )


def is_duplicate(news_id):

    state = load_state()

    return news_id in state["sent"]


def mark_sent(news_id):

    state = load_state()

    if news_id not in state["sent"]:

        state["sent"].append(news_id)

        state["sent"] = state["sent"][-100:]

        save_state(state)
