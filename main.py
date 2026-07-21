import os
import json
from groq import Groq
import requests
from bs4 import BeautifulSoup
from line import send_message

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

def fetch_facebook_mobile():
    # ใช้ Mobile Basic User Agent เพื่อให้ Facebook ส่ง HTML แบบเรียบง่ายที่สุดมาให้
    url = "https://mbasic.facebook.com/haydayhome1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        print(f"📖 กำลังสแกนหน้าเพจโดยตรงผ่าน Mobile Mode...")
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"⚠️ ไม่สามารถเข้าถึงหน้าเพจได้ Status: {r.status_code}")
            return None, None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # ค้นหาโพสต์บน mbasic facebook
        articles = soup.find_all('article') or soup.find_all('div', {'role': 'article'})
        
        for article in articles:
            text = article.get_text().strip()
            # ตัดข้อมูลสั้นหรือคำแนะนำตัวทั่วไปออก
            if len(text) > 30 and "Welcome to Hay Day Home" not in text:
                # สกัดเอาเฉพาะเนื้อหาหลัก
                clean_text = " ".join(text.split())
                print(f"✅ พบโพสต์ล่าสุด: {clean_text[:60]}...")
                return clean_text, clean_text[:100]

    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        
    return None, None

def main():
    print("====================================")
    print("🐔 Hay Day Bot (Mobile Scraper Mode)")
    print("====================================")
    
    post_text, raw_key = fetch_facebook_mobile()
    
    if not post_text:
        print("⏭️ ไม่พบเนื้อหาโพสต์ใหม่ ข้ามรอบนี้")
        print("====================================")
        return

    post_id = str(hash(raw_key))
    state = load_state()
    
    if state.get("last_fb_post") == post_id:
        print("⏭️ โพสต์ล่าสุดนี้เคยส่งเข้ากลุ่มไปแล้ว (ซ้ำ)")
        print("====================================")
        return

    print("🆕 พบโพสต์ใหม่! กำลังส่งให้ Groq AI แปลภาษา...")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวสารและกิจกรรมเกม Hay Day ภาษาไทย
    โปรดแปลและสรุปเนื้อหาจากโพสต์นี้ให้อ่านเข้าใจง่าย กระชับ และถูกต้อง:
    "{post_text[:1200]}"
    
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
    
    send_message(message)
    state["last_fb_post"] = post_id
    save_state(state)
    print("✅ ส่งข้อความเข้า LINE สำเร็จ!")
    print("====================================")

if __name__ == "__main__":
    main()
