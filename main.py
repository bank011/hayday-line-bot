from youtube import get_latest
from state import load, save
from line import send

state = load()

news = get_latest()

if news is None:
    print("No news")
    exit()

last = state.get(news["source"])

if last == news["id"]:
    print("Already sent")
    exit()

send(
    f"""📢 {news['source']}

{news['title']}

{news['link']}
"""
)

state[news["source"]] = news["id"]

save(state)

print("Done")
