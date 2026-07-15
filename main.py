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
            temperature=0.3, # ลด Temp ให้ AI สรุปข้อมูลนิ่งขึ้น ไม่เดาเนื้อหาเอง
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return None

def check_facebook():
    print("📖 Checking Facebook for Weekly Events...")
    fb_feed_url = "https://rss.app/feeds/v1/web/r1v8k7y3q8p2k5z8" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    post_text = ""
    post_url = "https://www.facebook.com/haydayhome1"
    image_url = ""

    try:
        response = requests.get(fb_feed_url, headers=headers, timeout=15)
        feed = feedparser.parse(response.content)
        if feed.entries:
            latest_entry = feed.entries[0]
            post_url = latest_entry.get("link", post_url)
            
            # ดึงเนื้อหา HTML เพื่อค้นหารูปภาพและข้อความประกอบ
            soup_content = BeautifulSoup(latest_entry.get("summary", latest_entry.get("description", "")), "html.parser")
            post_text = soup_content.get_text().strip()
            
            # ค้นหาลิงก์รูปภาพตารางกิจกรรม (มักจะอยู่ในแท็ก img)
            img_tag = soup_content.find("img")
            if img_tag and img_tag.get("src"):
                image_url = img_tag["src"]
    except Exception as e:
        print(f"⚠️ ดึงข้อมูลฟีดล้มเหลว: {e}")

    # หากดึงผ่าน RSS ไม่ได้ ให้ข้ามไปก่อนเพื่อรอรอบถัดไป
    if not post_text:
        print("⏭️ Facebook: ยังไม่พบโพสต์ใหม่ ข้ามรอบนี้")
        return None, None

    # บล็อกข้อมูลทั่วไปที่ไม่ใช่ตารางกิจกรรม
    if "ตารางกิจกรรม" not in post_text and "Event" not in post_text and "calendar" not in post_text.lower() and not image_url:
        print("⏭️ โพสต์ล่าสุดไม่ใช่ตารางกิจกรรมประจำสัปดาห์ ข้ามการทำงาน")
        return None, None

    post_id = str(hash(post_url))

    state = load_state()
    if state.get("last_fb_post") == post_id:
        print("⏭️ Facebook: ตารางกิจกรรมนี้เคยส่งไปแล้ว")
        return None, None

    print(f"🆕 พบตารางกิจกรรมใหม่! กำลังส่งให้ Groq AI แปลผล...")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปตารางกิจกรรมรายสัปดาห์ของเกม Hay Day เป็นภาษาไทย
    นี่คือข้อมูลเนื้อหาและบริบทของโพสต์ล่าสุด:
    "{post_text[:600]}"
    
    โปรดสรุปตารางกิจกรรมนี้ออกมาให้สมาชิกในไลน์กลุ่มอ่านง่าย โดยแบ่งเป็นรายวัน (จันทร์ - อาทิตย์) ตามข้อมูลที่ปรากฏในโพสต์:
    
    🌾 [สรุปหัวข้อ: ตารางกิจกรรมประจำสัปดาห์วันที่เท่าไหร่ถึงเท่าไหร่]
    ----------------------------------
    📅 รายละเอียดกิจกรรมประจำสัปดาห์:
    • วันจันทร์: [กิจกรรม]
    • วันอังคาร: [กิจกรรม]
    • วันพุธ: [กิจกรรม]
    • วันพฤหัสบดี: [กิจกรรม]
    • วันศุกร์: [กิจกรรม]
    • วันเสาร์: [กิจกรรม]
    • วันอาทิตย์: [กิจกรรม]
    ----------------------------------
    💡 แนะนำสมาชิกฟาร์ม: [ทริคสั้นๆ เช่น วันไหนควรดองของ วันไหนควรปั๊มเลเวล]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 พบอัปเดตตารางกิจกรรมใหม่จาก Hay Day เพจหลักแล้วครับ!"

    # ส่งเฉพาะข้อความสรุปแปลไทยตามที่คุณต้องการ (ไม่มีรูปภาพแนบไปใน LINE เพื่อความเสถียร)
    message = f"{summary}\n\n🔗 ลิงก์โพสต์ต้นฉบับเพื่อดูตารางรูปภาพ:\n{post_url}\n\n🤖 Powered by Hay Day AI News Bot"
    return message, post_id

def main():
    print("====================================")
    print("🐔 Hay Day Event Calendar Bot (Groq AI)")
    print("====================================")
    
    state = load_state()
    state_changed = False

    fb_message, fb_id = check_facebook()
    if fb_message:
        send_message(fb_message)
        state["last_fb_post"] = fb_id
        state_changed = True
        print("✅ ส่งสรุปตารางกิจกรรมเข้ากลุ่ม LINE สำเร็จ!")
    print("====================================")

    if state_changed:
        save_state(state)
        print("💾 บันทึกประวัติลง state.json เรียบร้อย")
        
    print("🚀 DONE ALL PROCESS")

if __name__ == "__main__":
    main()
