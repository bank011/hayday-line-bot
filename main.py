import os
import hashlib
import json
import re
from groq import Groq
import requests
from line import send_message

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")

client = Groq(api_key=GROQ_API_KEY)
HISTORY_FILE = "history.json"

def load_history_local():
    """อ่านประวัติโพสต์จากไฟล์ history.json ในเครื่อง"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"⚠️ Load local history error: {e}")
    return []

def save_history_local(history_list):
    """บันทึกประวัติโพสต์ลงไฟล์ history.json (เก็บย้อนหลัง 50 รายการ)"""
    try:
        updated_history = history_list[-50:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_history, f, ensure_ascii=False, indent=2)
        print(f"💾 บันทึกประวัติลงไฟล์สำเร็จ (รวม {len(updated_history)} รายการ)")
    except Exception as e:
        print(f"⚠️ Save local history error: {e}")

def generate_strict_post_id(text_content):
    clean_text = re.sub(r'[^a-zA-Z0-9ก-๙]', '', text_content)
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
    print("🐔 Hay Day Bot (Local File History Mode)")
    print("====================================")
    
    posts = fetch_all_recent_posts()
    
    if not posts:
        print("⏭️ ไม่พบรายการโพสต์ใดๆ จากเพจ ข้ามรอบนี้")
        print("====================================")
        return

    # ดึงประวัติจากไฟล์ในเครื่อง
    history = load_history_local()
    print(f"🔍 จำนวนประวัติโพสต์ในเครื่อง: {len(history)} รายการ")
    
    target_post = None
    target_post_id = ""

    for p in posts:
        current_id = generate_strict_post_id(p["text"])
        
        if current_id in history:
            print(f"🛑 โพสต์นี้เคยส่งแล้ว -> ข้าม: {p['text'][:30]}...")
            continue
            
        if not target_post:
            target_post = p
            target_post_id = current_id

    if not target_post:
        print("⏭️ ทุกโพสต์ล่าสุดเคยถูกส่งไปแล้ว (ปลอดการส่งซ้ำ 100%)")
        print("====================================")
        return

    print(f"🆕 พบโพสต์ใหม่จริงๆ! กำลังส่งให้ Groq AI สรุป...")
    
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
    
    # บันทึกรหัสลงประวัติในเครื่อง
    history.append(target_post_id)
    save_history_local(history)
    print("✅ ส่งข้อความเข้า LINE สำเร็จ และบันทึกประวัติลงไฟล์สำเร็จ!")
    print("====================================")

if __name__ == "__main__":
    main()
