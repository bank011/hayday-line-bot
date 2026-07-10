from youtube import get_latest_video
from ai import summarize
from line import send_message
from state import is_sent, mark


def main():

    print("=" * 60)
    print("🌾 Hay Day Home Bot")
    print("=" * 60)

    video = get_latest_video()

    if video is None:
        print("❌ ไม่พบวิดีโอ")
        return

    print(f"Latest : {video['title']}")
    print(f"ID     : {video['id']}")

    # เช็กว่าส่งไปแล้วหรือยัง
    if is_sent(video["id"]):
        print("✅ ส่งไปแล้ว")
        return

    print("🤖 กำลังสรุปด้วย AI...")

    result = summarize(video)

    if result.strip().upper() == "SKIP":
        print("⏭ AI ข้ามข่าวนี้")
        mark(video["id"])
        return

    message = f"""{result}

━━━━━━━━━━━━━━━━━━━━━━

📺 รับชมวิดีโอต้นฉบับ

{video['link']}

🤖 Powered by Hay Day AI News Bot
"""

    print("📤 กำลังส่ง LINE...")

    send_message(message)

    print("💾 บันทึก state.json")

    mark(video["id"])

    print("✅ DONE")


if __name__ == "__main__":
    main()
