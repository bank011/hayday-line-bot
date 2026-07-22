import os
import hashlib
import re
from groq import Groq
import requests
from line import send_message

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")

client = Groq(api_key=GROQ_API_KEY)

# --- ระบบคลังเก็บประวัติโพสต์ย้อนหลังบน Apify Cloud (เก็บสูงสุด 50 โพสต์ล่าสุด) ---
APIFY_STORE_URL = f"https://api.apify.com/v2/key-value-stores/default/records/HAYDAY_POSTS_HISTORY?token={APIFY_TOKEN}"

def load_history_from_apify():
    """ดึงประวัติโพสต์ทั้งหมดที่เคยส่งไปแล้ว"""
    try:
        r = requests.get(APIFY_STORE_URL, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get("history", [])
    except Exception as e:
        print(f"⚠️ Load history error: {e}")
    return []

def save_history_to_apify(history_list):
    """บันทึกประวัติโพสต์ลง Cloud (เก็บย้อนหลังสูงสุด 50 รายการ)"""
    try:
        # ตัดประวัติให้เหลือไม่เกิน 50 รายการล่าสุด
        updated_history = history_list[-50:]
        payload = {"history": updated_history}
        r = requests.put(APIFY_STORE_URL, json=payload, timeout=10)
        if r.status_code in [200, 201]:
            print(f"☁️ บันทึกประวัติลง Cloud เรียบร้อย (รวมทั้งหมด {len(updated_history)} รายการ)")
    except Exception as e:
        print(f"⚠️ Save history error: {e}")

def generate_strict_post_id(text_content):
    """ทำความสะอาดข้อความ ลบสัญลักษณ์/เว้นวรรคออก เหลือเฉพาะตัวอักษรและตัวเลข แล้ว Hash"""
    # ลบอักขระพิเศษ เว้นวรรค และ Emoji ออก ให้เหลือแค่ตัวอักษรภาษาอังกฤษ ภาษาไทย และตัวเลข
    clean_text = re.sub(r'[^a-zA-Z0-9ก-๙]', '', text_content)
    # ตัดเอา 60 ตัวอักษรแรกมาทำ MD5
    short_text = clean_text[:60].lower()
    return hashlib.md5(short_text.encode("utf-8")).hexdigest()

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
        "resultsLimit": 5,
        "maxRequestRetries": 3
    }

    posts_list = []
    try:
        r = requests.post(url, json=payload, timeout=120)
        print(f"🔹 Apify Status Code: {r.status_code}")
        
        if r.status_code in [200, 201]:
            data = r.json()
            if data and len(data) > 0:
                for item in data:
                    text = item.get("text", "") or item.get("caption", "") or item.get("message", "") or item.get("description", "")
                    post_url = item.get("url", "") or item.get("postUrl", "") or item.get("canonicalUrl", "")
                    
                    if text and len(text.strip()) > 10:
                        posts_list.append({
                            "text": text.strip(),
                            "post_url": post_url
                        })
                print(f"✅ ดึงรายการโพสต์สำเร็จทั้งหมด {len(posts_list)} โพสต์")
    except Exception as e:
        print(f"⚠️ Apify Request Error: {e}")
        
    return posts_list

def main():
    print("====================================")
    print("🐔 Hay Day Bot (Strict History Deduplication)")
    print("====================================")
    
    posts = fetch_all_recent_posts()
    
    if not posts:
        print("⏭️ ไม่พบรายการโพสต์ใดๆ จากเพจ ข้ามรอบนี้")
        print("====================================")
        return

    # ดึงประวัติรหัสโพสต์ทั้งหมดที่เคยส่งไปแล้วจาก Cloud
    history = load_history_from_apify()
    print(f"🔍 จำนวนประวัติโพสต์ที่เคยบันทึกไว้ในระบบ: {len(history)} รายการ")
    
    target_post = None
    target_post_id = ""

    # วนลูปเช็คโพสต์ทั้งหมด
    for p in posts:
        current_id = generate_strict_post_id(p["text"])
        
        # เช็คว่ารหัสนี้เคยอยู่ในประวัติหรือไม่
        if current_id in history:
            print(f"🛑 โพสต์นี้อยู่ในประวัติแล้ว (เคยส่งแล้ว) -> ข้าม: {p['text'][:30]}...")
            continue
            
        # ถ้าเจอบรรทัดที่ยังไม่เคยอยู่ในประวัติ ให้เลือกโพสต์นี้เป็นเป้าหมาย
        if not target_post:
            target_post = p
            target_post_id = current_id

    if not target_post:
        print("⏭️ ทุกโพสต์ใน 5 รายการล่าสุด ถูกบันทึกในประวัติหมดแล้ว (ข้ามการส่งซ้ำเด็ดขาด 100%)")
        print("====================================")
        return

    print(f"🆕 พบโพสต์ใหม่จริงๆ ที่ไม่เคยส่งมาก่อน! กำลังส่งให้ Groq AI สรุป...")
    
    post_text = target_post["text"]
    post_url = target_post["post_url"]
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวสารเกม Hay Day สำหรับส่งเข้ากลุ่ม LINE ภาษาไทย
    หน้าที่ของคุณ: แปลและสรุปเนื้อหาด้านล่างนี้ให้เป็นภาษาไทยที่อ่านง่าย สละสลวย เข้าใจทันที (ห้ามแปลตรงตัวแบบภาษาอังกฤษ)

    เนื้อหาต้นฉบับ:
    "{post_text[:1200]}"

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
        summary = f"🌾 Hay Day Home (อัปเดตโพสต์ใหม่)\n📢 โพสต์ใหม่: {post_text[:200]}..."

    message = f"{summary}\n\n🤖 Powered by Hay Day AI News Bot"
    if post_url:
        message += f"\n🔗 ดูโพสต์ต้นฉบับ: {post_url}"
    
    send_message(message)
    
    # เพิ่มรหัสโพสต์ใหม่ลงในประวัติ แล้วเซฟกลับลง Cloud
    history.append(target_post_id)
    save_history_to_apify(history)
    print("✅ ส่งข้อความเข้า LINE สำเร็จ และบันทึกรหัสลงคลังประวัติเรียบร้อย!")
    print("====================================")

if __name__ == "__main__":
    main()
