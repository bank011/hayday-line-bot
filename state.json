import json
import os

STATE_FILE = "state.json"


def load():

    if not os.path.exists(STATE_FILE):
        return {"last_video": ""}

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save(data):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def is_sent(video_id):

    data = load()

    return data.get("last_video") == video_id


def mark(video_id):

    data = load()

    data["last_video"] = video_id

    save(data)
