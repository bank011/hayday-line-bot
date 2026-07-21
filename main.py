import os
import hashlib
from groq import Groq
import requests
from line import send_message

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")

client = Groq(api_key=GROQ_API_KEY)

# --- ระบบบันทึกและอ่าน State บน Apify Cloud Storage ---
APIFY_STORE_URL = f"https://api.apify.com/v2/key-value-stores/default/records/HAYDAY_LAST_POST?token={APIFY_TOKEN}"

def load_state_from_apify():
    try:
        r = requests.get(APIFY_STORE_URL, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("last_fb_post", "")
    except Exception as e:
        print(f"⚠️ Load state error: {e}")
    return ""

def save_state_to_apify(post_id):
    try:
        payload = {"last_fb_post": post_id}
        r = requests.put(APIFY_STORE_URL, json=payload, timeout=10)
        if r.status_code in [200, 201]:
            print("☁️ บันทึก State ลง Apify Cloud สำเร็จ!")
    except Exception as e:
        print(f"⚠️ Save state error: {e}")

def generate_post_id(text):
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
    except Exception as e:
        print(f"⚠️ Apify Request Error: {e}")
        
    return posts_list

def main():
    print("====================================")
    print("🐔 Hay Day Bot (Apify Cloud State Storage)")
    print("====================================")
    
    posts = fetch_all_recent_posts()
    
    if not posts:
        print("⏭️ ไม่พบรายการโพสต์ใดๆ จากเพจ ข้ามรอบนี้")
        print("====================================")
        return

    # อ่านค่าโพสต์ล่าสุดจาก Apify Cloud
    last_saved_id = load_state_from_apify()
    print(f"🔍 รหัสโพสต์ล่าสุดที่เคยบันทึกไว้ในระบบ: {last_saved_id}")
    
    target_post = None
    target_post_id = ""

    for p in posts:
        current_id = generate_post_id(p["key"])
        
        # ถ้าเจอโพสต์ที่ตรงกับรหัสบน Cloud แสดงว่าเคยส่งแล้ว
        if current_id == last_saved_id:
            break
            
        if not target_post:
            target_post = p["text"]
            target_post_id = current_id

    if not target_post:
        print("⏭️ โพสต์นี้บันทึกอยู่บน Cloud เรียบร้อยแล้ว (ข้ามการส่งซ้ำชัวร์ 100%)")
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
    
    # บันทึกรหัสโพสต์ลง Apify Cloud ทันที
    save_state_to_apify(target_post_id)
    print("✅ ส่งข้อความเข้า LINE สำเร็จ และเซฟสเตทลง Cloud เรียบร้อย!")
    print("====================================")

if __name__ == "__main__":
    main()
