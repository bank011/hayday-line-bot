import os
import json
import hashlib
from groq import Groq
import requests
from line import send_message

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")

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

def generate_post_id(text):
    # ใช้ MD5 เพื่อให้รหัส Hash คงเดิมเสมอไม่ว่าจะรันรอบไหน
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def ask_groq(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return None

def fetch_all_recent_posts():
    print("📖 กำลังดึงรายการโพสต์ทั้งหมดล่าสุดจากเพจผ่าน Apify...")
    if not APIFY_TOKEN:
        print("⚠️ ยังไม่ได้ใส่ APIFY_TOKEN ในระบบ")
        return []

    url = f"https://api.apify.com/v2/acts/apify~facebook-posts-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}"
    payload = {
        "startUrls": [{"url": "https://www.facebook.com/haydayhome1"}],
        "resultsLimit": 5
    }

    posts_list = []
    try:
        r = requests.post(url, json=payload, timeout=120)
        print(f"🔹 Apify Status Code: {r.status_code}")
        
        if r.status_code in [200, 201]:
            data = r.json()
            if data and len(data) > 0:
                for item in data:
                    text = item.get("text", "") or item.get("caption", "") or item.get("message", "")
                    url_link = item.get("url", "") or item.get("postUrl", "") or item.get("canonicalUrl", "")
                    
                    if text and len(text.strip()) > 10:
                        posts_list.append({
                            "text": text.strip(),
                            "key": url_link or text.strip()[:100]
                        })
                print(f"✅ ดึงรายการโพสต์สำเร็จทั้งหมด {len(posts_list)} โพสต์")
            else:
                print("⚠️ Apify ส่งข้อมูลกลับมาเป็นรายการว่างเปล่า")
        else:
            print(f"⚠️ Apify Error Response: {r.text[:200]}")
    except Exception as e:
        print(f"⚠️ Apify Request Error: {e}")
        
    return posts_list

def main():
    print("====================================")
    print("🐔 Hay Day Bot (MD5 Deduplication Mode)")
    print("====================================")
    
    posts = fetch_all_recent_posts()
    
    if not posts:
        print("⏭️ ไม่พบรายการโพสต์ใดๆ จากเพจ ข้ามรอบนี้")
        print("====================================")
        return

    state = load_state()
    last_saved_id = state.get("last_fb_post", "")
    
    target_post = None
    target_post_id = ""

    # ตรวจสอบหาโพสต์ใหม่โดยเทียบ MD5 ID
    for p in posts:
        current_id = generate_post_id(p["key"])
        
        if current_id == last_saved_id:
            break
            
        if not target_post:
            target_post = p["text"]
            target_post_id = current_id

    if not target_post:
        print("⏭️ ทุกโพสต์ล่าสุดเคยถูกส่งเข้า LINE แล้ว (ข้ามการส่งซ้ำ)")
        print("====================================")
        return

    print(f"🆕 พบโพสต์ใหม่จริง! กำลังส่งให้ Groq AI สรุป...")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวสารเกม Hay Day สำหรับส่งเข้ากลุ่ม LINE ภาษาไทย
    หน้าที่ของคุณ: แปลและสรุปเนื้อหาด้านล่างนี้ให้เป็นภาษาไทยที่อ่านง่าย สละสลวย เข้าใจทันที (ห้ามแปลตรงตัวแบบภาษาอังกฤษ)

    เนื้อหาต้นฉบับ:
    "{target_post[:1200]}"

    ข้อกำหนดการตอบ:
    1. ใช้ภาษาไทยที่เป็นธรรมชาติ สละสลวย อ่านแล้วเก็ททันที
    2. คำศัพท์เกมให้ใช้ทับศัพท์ที่คนเล่นเข้าใจ เช่น บูสเตอร์ (Booster), เพชร (Diamond), อีเวนต์ (Event), เหรียญ (Gold)
    3. ห้ามมีอักขระพิเศษ สระซ้อน หรือกล่องข้อความเพี้ยนๆ ปรากฏในข้อความ

    ให้จัดรูปแบบผลลัพธ์ตามนี้เท่านั้น:
    🌾 Hay Day Home (อัปเดตโพสต์ใหม่)
    ----------------------------------
    📢 ข่าวสาร/โพสต์: [สรุปสั้นๆ ว่ามีกิจกรรมหรืออัปเดตอะไร]
    📝 เนื้อหาหลัก: [อธิบายรายละเอียด 2-3 บรรทัดด้วยภาษาไทยที่สละสลวย]
    🎯 สิ่งที่ต้องรู้/แนะนำ: [บอกทริคหรือสิ่งที่ผู้เล่นควรทำในเกม]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 Hay Day Home (อัปเดตโพสต์ใหม่)\n📢 โพสต์ใหม่: {target_post[:200]}..."

    message = f"{summary}\n\n🤖 Powered by Hay Day AI News Bot"
    
    send_message(message)
    state["last_fb_post"] = target_post_id
    save_state(state)
    print("✅ ส่งข้อความเข้า LINE สำเร็จ และบันทึก ID ลง state.json เรียบร้อย!")
    print("====================================")

if __name__ == "__main__":
    main()
