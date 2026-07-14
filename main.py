from youtube import get_latest_video
from facebook import get_latest_fb_post
from ai import summarize, summarize_facebook
from line import send_message
import state

def process_youtube():
    print("📺 Checking YouTube...")
    video = get_latest_video()
    if video is None:
        print("❌ ไม่พบวิดีโอ")
        return

    if state.is_youtube_sent(video["id"]):
        print("✅ วิดีโอนี้ส่งไปแล้ว")
        return

    print("🤖 กำลังสรุปวิดีโอด้วย AI...")
    result = summarize(video)
    if result.strip().upper() == "SKIP":
        state.mark_youtube(video["id"])
        return

    message = f"{result}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n📺 รับชมวิดีโอต้นฉบับ\n\n{video['link']}\n\n🤖 Powered by Hay Day AI News Bot"
    send_message(message)
    state.mark_youtube(video["id"])
    print("✅ ทำงานฝั่ง YouTube สำเร็จ")


def process_facebook():
    print("📖 Checking Facebook...")
    post = get_latest_fb_post()
    if post is None:
        print("❌ ไม่พบโพสต์เฟสบุ๊ค")
        return

    if state.is_facebook_sent(post["id"]):
        print("✅ โพสต์เฟสบุ๊คนี้ส่งไปแล้ว")
        return

    print("🤖 กำลังแปลและสรุปโพสต์ด้วย AI...")
    result = summarize_facebook(post)

    message = f"{result}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n🔗 ลิงก์โพสต์ต้นฉบับ\n\n{post['link']}\n\n🤖 Powered by Hay Day AI News Bot"
    send_message(message)
    state.mark_facebook(post["id"])
    print("✅ ทำงานฝั่ง Facebook สำเร็จ")


def main():
    print("=" * 60)
    print("🌾 Hay Day Home Bot (YouTube & Facebook)")
    print("=" * 60)
    
    # รันตรวจสอบทั้งสองช่องทางพร้อมกันในรอบนั้นๆ
    process_youtube()
    print("-" * 60)
    process_facebook()
    print("=" * 60)
    print("🚀 DONE ALL PROCESS")

if __name__ == "__main__":
    main()
