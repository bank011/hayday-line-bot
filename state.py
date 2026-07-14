import json
import os

STATE_FILE = "state.json"

def load():
    if not os.path.exists(STATE_FILE):
        return {"last_video": "", "last_fb_post": ""} # เพิ่มคีย์ของเฟสบุ๊คไว้รองรับ
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- ส่วนของ YouTube ---
def is_youtube_sent(video_id):
    data = load()
    return data.get("last_video") == video_id

def mark_youtube(video_id):
    data = load()
    data["last_video"] = video_id
    save(data)

# --- ส่วนของ Facebook ---
def is_facebook_sent(post_id):
    data = load()
    return data.get("last_fb_post") == post_id

def mark_facebook(post_id):
    data = load()
    data["last_fb_post"] = post_id
    save(data)
