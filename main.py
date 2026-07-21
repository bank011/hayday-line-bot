import os
import json
from groq import Groq
import requests
from line import send_message

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "") # ใส่ Token จาก Apify ใน Secrets

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

def fetch_via_apify():
    print("📖 กำลังดึงข้อมูลโพสต์ล่าสุดผ่าน Apify Service...")
    if not APIFY_TOKEN:
        print("⚠️ ยังไม่ได้ใส่ APIFY_TOKEN ในระบบ")
        return None, None

    # เรียกใช้ Apify Facebook Page Scraper Actor
    url = f"https://api.apify.com/v2/acts/apify~facebook-page-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}"
    payload = {
        "startUrls": [{"url": "https://www.facebook.com/haydayhome1"}],
        "maxPosts": 1
    }

    try:
        r = requests.post(url, json=payload, timeout=60)
        if r.status_code == 201 or r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                post = data[0]
                post_text = post.get("text", "") or post.get("caption", "")
                post_url = post.get("url", "") or post.get("postUrl", "")
                print(f"✅ Apify ดึงโพสต์สำเร็จ: {post_text[:60]}...")
                return post_text, post_url
    except Exception as e:
        print(f"⚠️ Apify Error: {e}")
        
    return None, None

def main():
    print("====================================")
    print("🐔 Hay Day Bot (Apify Cloud Scraper)")
    print("====================================")
    
    post_text, post_url = fetch_via_apify()
    
    if not post_text:
        print("⏭️ ไม่พบเนื้อหาโพสต์ใหม่ ข้ามรอบนี้")
        print("====================================")
        return

    post_id = str(hash(post_url or post_text[:100]))
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
