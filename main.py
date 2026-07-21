import os
import json
from groq import Groq
import requests
from bs4 import BeautifulSoup
import feedparser
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
    return {"last_fb_post": ""}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def ask_groq(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return None

def fetch_feed_data():
    # รายชื่อแหล่งฟีดเรียงตามความเร็ว (RSSHub ก่อน ถ้าไม่ผ่านจะไป RSS.app)
    feed_urls = [
        "https://rsshub.app/facebook/page/haydayhome1",
        "https://rss.app/feeds/1zNu9ZwSfalDdaUs.xml"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for url in feed_urls:
        print(f"📖 กำลังลองดึงข้อมูลจาก: {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                if feed.entries:
                    for entry in feed.entries:
                        soup_content = BeautifulSoup(entry.get("summary", entry.get("description", "")), "html.parser")
                        text_check = soup_content.get_text().strip()
                        
                        # ข้ามข้อมูลแนะนำตัวเพจ
                        if "Welcome to Hay Day Home" in text_check or "Official Supercell Creator" in text_check:
                            continue
                        
                        if len(text_check) > 5:
                            unique_key = entry.get("id", entry.get("link", text_check[:100]))
                            print("✅ ดึงข้อมูลสำเร็จ!")
                            return text_check, unique_key
        except Exception as e:
            print(f"⚠️ ลองฟีดนี้ไม่สำเร็จ: {e}")

    return None, None

def check_facebook():
    post_text, post_unique_key = fetch_feed_data()

    if not post_text:
        print("⏭️ ไม่พบเนื้อหาโพสต์ใหม่จากทุกแหล่ง ข้ามรอบนี้")
        return None, None

    post_id = str(hash(post_unique_key))

    state = load_state()
    if state.get("last_fb_post") == post_id:
        print("⏭️ โพสต์ล่าสุดนี้เคยส่งเข้ากลุ่มไปแล้ว (ล็อกอยู่)")
        return None, None

    print(f"🆕 พบโพสต์ใหม่! กำลังส่งให้ AI สรุป...")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวสารและกิจกรรมเกม Hay Day ภาษาไทย
    โปรดแปลและสรุปเนื้อหาจากโพสต์นี้ให้อ่านเข้าใจง่าย กระชับ และถูกต้อง:
    "{post_text[:1000]}"
    
    กำหนดรูปแบบผลลัพธ์ใน LINE:
    🌾 Hay Day Home (อัปเดตโพสต์ใหม่)
    ----------------------------------
    📢 ข่าวสาร/โพสต์: [สรุปหัวข้อหลักของโพสต์นี้เป็นภาษาไทย]
    📝 เนื้อหาหลัก: [สรุปใจความสำคัญรายละเอียด 2-3 บรรทัด]
    🎯 สิ่งที่ต้องรู้/แนะนำ: [สรุปทริคหรือสิ่งที่ผู้เล่นต้องทำจากโพสต์นี้]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 Hay Day Home (อัปเดตโพสต์ใหม่)\n📢 โพสต์ใหม่: {post_text[:200]}..."

    message = f"{summary}\n\n🤖 Powered by Hay Day AI News Bot"
    return message, post_id

def main():
    print("====================================")
    print("🐔 Hay Day Bot (Multi-Feed Fallback Mode)")
    print("====================================")
    
    fb_message, fb_id = check_facebook()
    if fb_message:
        send_message(fb_message)
        state = load_state()
        state["last_fb_post"] = fb_id
        save_state(state)
        print("✅ ส่งข้อความเข้า LINE สำเร็จ!")
    else:
        print("⏭️ จบกระบวนการ (ไม่มีโพสต์ใหม่)")
    print("====================================")

if __name__ == "__main__":
    main()
