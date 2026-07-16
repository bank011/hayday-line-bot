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

def check_facebook_rss():
    print("📖 Checking Facebook via RSS.app XML Link...")
    fb_feed_url = "https://rss.app/feeds/1zNu9ZwSfalDdaUs.xml" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    post_text = ""
    post_unique_key = ""

    try:
        response = requests.get(fb_feed_url, headers=headers, timeout=15)
        feed = feedparser.parse(response.content)
        
        if feed.entries:
            for entry in feed.entries:
                soup_content = BeautifulSoup(entry.get("summary", entry.get("description", "")), "html.parser")
                text_check = soup_content.get_text().strip()
                
                # ข้ามข้อมูลทั่วไปของเพจ
                if "Welcome to Hay Day Home" in text_check or "Official Supercell Creator" in text_check or "เป็นหน้าแฟนเพจ" in text_check:
                    print("⏭️ ข้ามข้อมูลแนะนำตัวเพจหลัก...")
                    continue
                
                if len(text_check) > 5:
                    post_text = text_check
                    # 🔒 ใช้ค่า ID แท้ของระบบ RSS หรือ ลิงก์ยาวตัวเต็มมาทำคีย์ล็อก เพื่อไม่ให้เกิดรหัสซ้ำ
                    post_unique_key = entry.get("id", entry.get("link", text_check[:150]))
                    break
    except Exception as e:
        print(f"⚠️ ดึงข้อมูลฟีดล้มเหลว: {e}")

    if not post_text:
        print("⏭️ Facebook: ไม่พบเนื้อหาโพสต์ใหม่ ข้ามรอบนี้")
        return None, None

    # แปลงคีย์ล็อกโพสต์ให้อยู่ในรูปแบบไอดีปลอดภัย
    post_id = str(hash(post_unique_key))

    state = load_state()
    if state.get("last_fb_post") == post_id:
        print("⏭️ Facebook: โพสต์ล่าสุดนี้เคยส่งเข้ากลุ่มไปแล้ว (ล็อกอยู่)")
        return None, None

    print(f"🆕 พบโพสต์ใหม่จาก RSS! กำลังส่งให้ Groq AI แปลผล...")
    
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
    print("🐔 Hay Day Bot (RSS.app Strict Lock Mode)")
    print("====================================")
    
    fb_message, fb_id = check_facebook_rss()
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
