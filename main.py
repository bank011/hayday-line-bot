import os
import json
from groq import Groq
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

def check_facebook_direct():
    print("📖 Checking Facebook Directly (All Posts)...")
    url = "https://www.facebook.com/haydayhome1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # ค้นหาข้อความจากโครงสร้างหน้าเว็บ
        articles = soup.find_all("div", {"data-ad-comet-preview": "message"})
        if not articles:
            articles = soup.find_all("div", {"dir": "auto"})

        latest_post = ""
        for a in articles:
            text = a.get_text().strip()
            # เอาทุกโพสต์ที่ยาวเกิน 5 ตัวอักษรขึ้นไป โดยไม่ตัดคำใดๆ ออกทั้งสิ้น
            if len(text) > 5:
                latest_post = text
                break
        
        if not latest_post:
            # แผนสำรองดึงจาก meta description หากโครงสร้างหลักดึงไม่ได้
            meta = soup.find("meta", property="og:description")
            if meta and len(meta["content"]) > 5:
                latest_post = meta["content"].strip()
        
        if not latest_post:
            print("⏭️ ไม่สามารถดึงข้อความจากหน้าเว็บได้")
            return None, None

        # สร้างไอดีจากเนื้อหาโพสต์เพื่อเช็คการส่งซ้ำ
        post_id = str(hash(latest_post[:100]))
        
        state = load_state()
        if state.get("last_fb_post") == post_id:
            print("⏭️ โพสต์ล่าสุดนี้เคยส่งเข้ากลุ่มแล้ว (ซ้ำ)")
            return None, None
            
        print(f"🆕 พบโพสต์ใหม่เตรียมประมวลผล: {latest_post[:50]}...")
        
        prompt = f"""
        คุณคือผู้ช่วยสรุปโพสต์จากเพจ Hay Day Home เป็นภาษาไทย
        โปรดแปลและสรุปเนื้อหาจากโพสต์นี้ให้อ่านเข้าใจง่ายและกระชับ:
        "{latest_post[:1000]}"
        
        กำหนดรูปแบบการแสดงผลใน LINE:
        🌾 Hay Day Home (อัปเดตโพสต์ใหม่)
        ----------------------------------
        📢 ข่าวสาร/โพสต์: [สรุปหัวข้อหลักของโพสต์นี้เป็นภาษาไทย]
        📝 เนื้อหาหลัก: [สรุปใจความสำคัญรายละเอียด 2-3 บรรทัด]
        🎯 สิ่งที่ต้องรู้/แนะนำ: [สรุปทริคหรือคำแนะนำจากโพสต์นี้]
        """
        
        message = ask_groq(prompt)
        if not message:
            message = f"🌾 Hay Day Home (อัปเดตโพสต์ใหม่)\n📢 โพสต์ใหม่: {latest_post[:200]}..."
            
        message = f"{message}\n\n🤖 Powered by Hay Day AI News Bot"
        return message, post_id

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None, None

def main():
    print("====================================")
    print("🐔 Hay Day Direct Bot (All Posts Mode)")
    print("====================================")
    
    fb_message, fb_id = check_facebook_direct()
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
