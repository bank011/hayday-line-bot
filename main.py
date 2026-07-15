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
            temperature=0.4,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return None

def check_facebook():
    print("📖 Checking Facebook for Real Posts...")
    # ใช้ลิงก์ฟีด XML ปัจจุบันของคุณ
    fb_feed_url = "https://rss.app/feeds/1zNu9ZwSfalDdaUs.xml" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    post_text = ""
    post_url = "https://www.facebook.com/haydayhome1"

    try:
        response = requests.get(fb_feed_url, headers=headers, timeout=15)
        feed = feedparser.parse(response.content)
        
        if feed.entries:
            for entry in feed.entries:
                soup_content = BeautifulSoup(entry.get("summary", entry.get("description", "")), "html.parser")
                text_check = soup_content.get_text().strip()
                
                if "Welcome to Hay Day Home" in text_check or "Official Supercell Creator" in text_check or "เป็นหน้าแฟนเพจ" in text_check:
                    print("⏭️ ข้ามข้อมูลแนะนำตัวเพจหลัก...")
                    continue
                
                if len(text_check) > 5:
                    post_text = text_check
                    post_url = entry.get("link", post_url)
                    break
    except Exception as e:
        print(f"⚠️ ดึงข้อมูลฟีดล้มเหลว: {e}")

    if not post_text:
        print("⏭️ Facebook: ไม่พบเนื้อหาโพสต์กิจกรรมใหม่ ข้ามรอบนี้")
        return None, None

    post_id = str(hash(post_url + post_text[:40]))

    state = load_state()
    if state.get("last_fb_post") == post_id:
        print("⏭️ Facebook: โพสต์ล่าสุดนี้เคยส่งเข้ากลุ่มไปแล้ว")
        return None, None

    print(f"🆕 พบโพสต์กิจกรรมของจริงแล้ว! กำลังส่งให้ Groq AI แปลผล...")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวสารและกิจกรรมเกม Hay Day ภาษาไทย
    โปรดแปลและสรุปเนื้อหาจากโพสต์ของเพจทางการนี้ให้แฟนเพจชาวไทยอ่านเข้าใจง่าย กระชับ และถูกต้อง:
    "{post_text[:800]}"
    
    กำหนดรูปแบบผลลัพธ์ใน LINE ให้สวยงาม:
    🌾 Hay Day Home (อัปเดตกิจกรรม)
    ----------------------------------
    📢 ข่าวสาร/กิจกรรม: [ชื่อกิจกรรมหรือหัวข้อภาษาไทยสรุปสั้นๆ]
    📝 รายละเอียด: [เนื้อหาใจความสำคัญย่อเหลือ 2-3 บรรทัด ว่าโพสต์นี้แจกอะไร เกิดอะไรขึ้น หรือแจ้งเรื่องอะไร]
    🎯 ทริก/สิ่งที่ต้องรู้: [สิ่งที่ผู้เล่นต้องทำหรือเตรียมตัวจากโพสต์นี้]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 Hay Day Home (อัปเดตกิจกรรม)\n📢 โพสต์ใหม่: {post_text[:200]}..."

    # ส่งเฉพาะข้อความสรุปและชื่อเพจ (ตัดส่วนแสดงลิงก์ URL ออกเรียบร้อย)
    message = f"{summary}\n\n🤖 Powered by Hay Day AI News Bot"
    return message, post_id

def main():
    print("====================================")
    print("🐔 Hay Day Home Bot (Groq AI Facebook-Only)")
    print("====================================")
    
    state = load_state()
    state_changed = False

    fb_message, fb_id = check_facebook()
    if fb_message:
        send_message(fb_message)
        state["last_fb_post"] = fb_id
        state_changed = True
        print("✅ ส่งสรุปกิจกรรมเข้ากลุ่ม LINE สำเร็จ!")
    print("====================================")

    if state_changed:
        save_state(state)
        print("💾 บันทึกประวัติลง state.json เรียบร้อย")
        
    print("🚀 DONE ALL PROCESS")

if __name__ == "__main__":
    main()
