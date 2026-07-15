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
    print("📖 Checking Facebook for Latest Events...")
    # ดึงข้อมูลผ่าน Feed ล่าสุดที่เสถียร
    fb_feed_url = "https://rss.app/feeds/1zNu9ZwSfaIDdaUs.xml" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    post_text = ""
    post_url = "https://www.facebook.com/haydayhome1"

    try:
        response = requests.get(fb_feed_url, headers=headers, timeout=15)
        feed = feedparser.parse(response.content)
        if feed.entries:
            latest_entry = feed.entries[0]
            post_url = latest_entry.get("link", post_url)
            
            soup_content = BeautifulSoup(latest_entry.get("summary", latest_entry.get("description", "")), "html.parser")
            post_text = soup_content.get_text().strip()
    except Exception as e:
        print(f"⚠️ ดึงข้อมูลฟีดล้มเหลว: {e}")

    # หากดึงผ่าน Feed ไม่สำเร็จ ให้ลองดึงจากหน้าเว็บตรง
    if not post_text:
        try:
            r = requests.get("https://www.facebook.com/haydayhome1", headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_desc = soup.find("meta", property="og:description")
            if meta_desc:
                post_text = meta_desc["content"].strip()
        except:
            pass

    # ดักจับถ้าไม่มีข้อความ หรือเป็นแค่คำอธิบายเพจทั่วไปให้ข้ามรอบ
    if not post_text or "เป็นหน้าแฟนเพจ" in post_text or "หน้าแฟนเพจที่มีเนื้อหา" in post_text:
        print("⏭️ Facebook: ไม่พบเนื้อหาโพสต์กิจกรรมใหม่ ข้ามรอบนี้")
        return None, None

    # สร้างรหัสตรวจสอบจากเนื้อหาโพสต์เพื่อป้องกันการส่งข้อความซ้ำ
    post_id = str(hash(post_url + post_text[:40]))

    state = load_state()
    if state.get("last_fb_post") == post_id:
        print("⏭️ Facebook: โพสต์กิจกรรมล่าสุดนี้เคยส่งเข้ากลุ่มแล้ว")
        return None, None

    print(f"🆕 พบโพสต์กิจกรรมใหม่! กำลังส่งให้ Groq AI แปลผล...")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวสารและกิจกรรมเกม Hay Day ภาษาไทย
    โปรดแปลและสรุปเนื้อหาจากโพสต์ Facebook นี้ให้แฟนเพจชาวไทยอ่านเข้าใจง่ายและกระชับ:
    "{post_text[:800]}"
    
    กำหนดรูปแบบผลลัพธ์ใน LINE ให้สวยงาม:
    🌾 Hay Day (Facebook อัปเดตกิจกรรม)
    ----------------------------------
    📢 ข่าวสาร/กิจกรรม: [ชื่อกิจกรรมหรือหัวข้อภาษาไทยสรุปสั้นๆ]
    📝 รายละเอียด: [เนื้อหาใจความสำคัญ 2-3 บรรทัด ว่าเป็นกิจกรรมอะไร วันไหน]
    🎯 ทริคสำหรับผู้เล่น: [ทริคเล็กๆ หรือสิ่งที่ผู้เล่นต้องเตรียมตัวทำในเกม]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 Hay Day (Facebook อัปเดต)\n📢 โพสต์ใหม่: {post_text[:200]}..."

    message = f"{summary}\n\n🔗 ลิงก์โพสต์ต้นฉบับ:\n{post_url}\n\n🤖 Powered by Hay Day AI News Bot"
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
