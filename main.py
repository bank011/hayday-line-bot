import os
import json
from groq import Groq
import feedparser
import requests
from bs4 import BeautifulSoup
from line import send_message

# ตั้งค่า Groq Client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"last_video": "", "last_fb_post": ""}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def ask_groq(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return None

def check_youtube():
    print("📺 Checking YouTube...")
    channel_id = "UC6qZ8kWG0KstK-V6d74E8rw"
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    video_id = None
    video_title = None
    video_url = None

    try:
        response = requests.get(feed_url, headers=headers, timeout=15)
        feed = feedparser.parse(response.content)
        if feed.entries:
            latest_entry = feed.entries[0]
            video_id = latest_entry.yt_videoid
            video_title = latest_entry.title
            video_url = latest_entry.link
    except Exception as e:
        print(f"⚠️ YouTube RSS ดึงไม่สำเร็จ: {e}")

    if not video_id:
        print("⏭️ YouTube: ดึงข้อมูลจริงไม่ได้ ข้ามการทำงานรอบนี้")
        return None, None

    state = load_state()
    if state.get("last_video") == video_id:
        print("⏭️ YouTube: ไม่มีวิดีโอใหม่")
        return None, None

    print(f"🆕 ประมวลผลวิดีโอ: {video_title}")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวเกม Hay Day ภาษาไทย
    โปรดสรุปและแปลเนื้อหาจากชื่อวิดีโอนี้: "{video_title}"
    
    กำหนดรูปแบบผลลัพธ์ให้เป็นข้อความสั้นๆ น่าอ่านใน LINE:
    🌾 Hay Day (YouTube อัปเดต)
    -------------------------
    📺 วิดีโอใหม่: [สรุปชื่อภาษาไทยแบบกระชับ]
    📝 รายละเอียด: [เขียนสรุปสั้นๆ 2-3 บรรทัดว่าคลิปนี้เกี่ยวกับอะไร]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 Hay Day (YouTube อัปเดต)\n📺 วิดีโอใหม่: {video_title}"

    message = f"{summary}\n\n🔗 รับชมวิดีโอฉบับเต็ม:\n{video_url}\n\n🤖 Powered by Hay Day AI News Bot"
    return message, video_id

def check_facebook():
    print("📖 Checking Facebook...")
    # เปลี่ยนมาใช้ช่องทาง Feed สำรองของ rss.app ที่ดึงข้อมูลโพสต์จริงได้แม่นยำกว่า
    fb_feed_url = "https://rss.app/feeds/v1/web/r1v8k7y3q8p2k5z8" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    post_text = ""
    post_url = "https://www.facebook.com/haydayhome1"

    try:
        response = requests.get(fb_feed_url, headers=headers, timeout=15)
        # ดึงผ่าน feedparser หากได้รับเป็นโครงสร้าง feed
        feed = feedparser.parse(response.content)
        if feed.entries:
            latest_entry = feed.entries[0]
            soup_content = BeautifulSoup(latest_entry.get("summary", latest_entry.get("description", "")), "html.parser")
            post_text = soup_content.get_text().strip()
            post_url = latest_entry.get("link", post_url)
        else:
            # แผนสำรองดึงแบบตรงผ่านหน้าเว็บ หาก RSS เจนเนอเรเตอร์ช้า
            r = requests.get("https://www.facebook.com/haydayhome1", headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_desc = soup.find("meta", property="og:description")
            if meta_desc and "แฟนเพจ" not in meta_desc["content"]:
                post_text = meta_desc["content"].strip()
    except Exception as e:
        print(f"⚠️ ดึง Facebook ผ่านฟีดสำรองไม่สำเร็จ: {e}")

    if not post_text:
        print("⏭️ Facebook: ไม่สามารถดึงโพสต์ล่าสุดได้ ข้ามการทำงานรอบนี้")
        return None, None

    # สร้างรหัสความต่างโพสต์จาก URL หรือ เนื้อหาข้อความ
    post_id = str(hash(post_url + post_text[:30]))

    state = load_state()
    if state.get("last_fb_post") == post_id:
        print("⏭️ Facebook: ไม่มีโพสต์ใหม่")
        return None, None

    print(f"🆕 ประมวลผลโพสต์ Facebook ใหม่สำเร็จ")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวเกม Hay Day ภาษาไทย
    โปรดแปลและสรุปเนื้อหาโพสต์ Facebook นี้ให้แฟนเพจชาวไทยอ่านเข้าใจง่าย:
    "{post_text[:800]}"
    
    กำหนดรูปแบบผลลัพธ์ใน LINE:
    🌾 Hay Day (Facebook อัปเดต)
    -------------------------
    🗓️ กิจกรรม / ข่าวสาร: [ชื่อกิจกรรมหรือหัวข้อภาษาไทยสรุปสั้นๆ]
    💡 สรุปเนื้อหา: [เนื้อหาใจความสำคัญ 2-3 บรรทัด]
    🎯 คำแนะนำสำหรับผู้เล่น: [ทริคเล็กๆ หรือสิ่งที่ต้องทำในเกมจากโพสต์นี้]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 Hay Day (Facebook อัปเดต)\n📢 โพสต์ใหม่: {post_text[:200]}..."

    message = f"{summary}\n\n🔗 ลิงก์เพจต้นฉบับ:\n{post_url}\n\n🤖 Powered by Hay Day AI News Bot"
    return message, post_id

def main():
    print("====================================")
    print("🐔 Hay Day Home Bot (Groq AI Text-Only)")
    print("====================================")
    
    state = load_state()
    state_changed = False

    # 1. ตรวจสอบ YouTube
    yt_message, yt_id = check_youtube()
    if yt_message:
        send_message(yt_message)
        state["last_video"] = yt_id
        state_changed = True
        print("✅ ทำงานฝั่ง YouTube สำเร็จ")
    print("------------------------------------")

    # 2. ตรวจสอบ Facebook
    fb_message, fb_id = check_facebook()
    if fb_message:
        send_message(fb_message)
        state["last_fb_post"] = fb_id
        state_changed = True
        print("✅ ทำงานฝั่ง Facebook สำเร็จ")
    print("====================================")

    if state_changed:
        save_state(state)
        print("💾 บันทึกประวัติสถานะใหม่เรียบร้อย")
        
    print("🚀 DONE ALL PROCESS")

if __name__ == "__main__":
    main()
