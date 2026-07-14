import os
import json
from groq import Groq
import feedparser
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
    return {"last_video": "", "last_fb_post": ""}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def ask_groq(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return None

def check_youtube():
    print("📺 Checking YouTube...")
    channel_id = "UC6qZ8kWG0KstK-V6d74E8rw"
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    
    # ส่ง User-Agent เพื่อป้องกันโดนบล็อกการดึง RSS
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(feed_url, headers=headers, timeout=15)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"❌ YouTube Request Error: {e}")
        return None, None, None

    if not feed.entries:
        print("❌ ไม่สามารถดึงข้อมูล YouTube RSS ได้")
        return None, None, None

    latest_entry = feed.entries[0]
    video_id = latest_entry.yt_videoid
    video_title = latest_entry.title
    video_url = latest_entry.link

    # 📸 ดึงลิงก์รูปหน้าปกวิดีโอ (Thumbnail) ความละเอียดสูงสูงสุด
    video_thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    state = load_state()
    if state.get("last_video") == video_id:
        print("⏭️ YouTube: ไม่มีวิดีโอใหม่")
        return None, None, None

    print(f"🆕 พบวิดีโอใหม่: {video_title}")
    
    prompt = f"""
    คุณคือผู้ช่วยสรุปข่าวเกม Hay Day ภาษาไทย
    โปรดสรุปและแปลเนื้อหาจากชื่อวิดีโอนี้: "{video_title}"
    
    กำหนดรูปแบบผลลัพธ์ให้เป็นข้อความสั้นๆ น่าอ่านใน LINE:
    🌾 Hay Day (YouTube อัปเดต)
    -------------------------
    📺 วิดีโอใหม่: [สรุปชื่อภาษาไทยแบบกระชับ]
    📝 รายละเอียด: [เขียนสรุปสั้นๆ 2-3 บรรทัดว่าคลิปนี้เกี่ยวกับอะไร]
    """
    
    summary = ask_groq(prompt)
    if not summary:
        summary = f"🌾 Hay Day (YouTube อัปเดต)\n📺 วิดีโอใหม่: {video_title}"

    message = f"{summary}\n\n🔗 รับชมวิดีโอฉบับเต็ม:\n{video_url}\n\n🤖 Powered by Hay Day AI News Bot"
    return message, video_thumbnail, video_id

def check_facebook():
    print("📖 Checking Facebook...")
    # ใช้ลิงก์แบบปกติแทน mobile เพื่อความเสถียรในการแกะ Open Graph รูปภาพ
    page_url = "https://www.facebook.com/haydayhome1/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "th-TH,th;q=0.9"
    }
    
    try:
        r = requests.get(page_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # ดึงรูปภาพและเนื้อหาหลักจาก Meta Tags ที่ Facebook เตรียมไว้ให้ (แม่นยำที่สุด ไม่หลุดง่าย)
        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")
        meta_image = soup.find("meta", property="og:image")
        
        post_text = meta_desc["content"].strip() if meta_desc else ""
        fb_image = meta_image["content"].strip() if meta_image else None
        
        if not post_text:
            # แผนสำรองหากดึง og tags ไม่เจอ
            post_element = soup.find('div', {'data-ft': True}) or soup.find('article')
            if not post_element:
                print("❌ ไม่พบโพสต์บนหน้า Facebook Page")
                return None, None, None
            post_text = post_element.text.strip()
            img_tag = post_element.find('img')
            if img_tag and img_tag.get('src'):
                fb_image = img_tag['src']

        # สร้าง ID จำลองจากเนื้อหา
        post_id = str(hash(post_text[:50]))

        state = load_state()
        if state.get("last_fb_post") == post_id:
            print("⏭️ Facebook: ไม่มีโพสต์ใหม่")
            return None, None, None

        print(f"🆕 พบโพสต์ Facebook ใหม่")
        
        prompt = f"""
        คุณคือผู้ช่วยสรุปข่าวเกม Hay Day ภาษาไทย
        โปรดแปลและสรุปเนื้อหาโพสต์ Facebook นี้ให้แฟนเพจชาวไทยอ่านเข้าใจง่าย:
        "{post_text[:800]}"
        
        กำหนดรูปแบบผลลัพธ์ใน LINE:
        🌾 Hay Day (Facebook อัปเดต)
        -------------------------
        🗓️ กิจกรรม / ข่าวสาร: [ชื่อกิจกรรมหรือหัวข้อภาษาไทยสรุปสั้นๆ]
        💡 สรุปเนื้อหา: [เนื้อหาใจความสำคัญ 2-3 บรรทัด]
        🎯 คำแนะนำสำหรับผู้เล่น: [ทริคเล็กๆ หรือสิ่งที่ต้องทำในเกมจากโพสต์นี้]
        """
        
        summary = ask_groq(prompt)
        if not summary:
            summary = f"🌾 Hay Day (Facebook อัปเดต)\n📢 โพสต์ใหม่: {post_text[:200]}..."

        message = f"{summary}\n\n🔗 ลิงก์เพจต้นฉบับ:\n{page_url}\n\n🤖 Powered by Hay Day AI News Bot"
        return message, fb_image, post_id
        
    except Exception as e:
        print(f"❌ Facebook Scraping Error: {e}")
        return None, None, None

def main():
    print("====================================")
    print("🐔 Hay Day Home Bot (Groq AI Version)")
    print("====================================")
    
    state = load_state()
    state_changed = False

    # 1. ตรวจสอบ YouTube
    yt_message, yt_image, yt_id = check_youtube()
    if yt_message:
        send_message(yt_message, image_url=yt_image)
        state["last_video"] = yt_id
        state_changed = True
        print("✅ ทำงานฝั่ง YouTube สำเร็จ")
    print("------------------------------------")

    # 2. ตรวจสอบ Facebook
    fb_message, fb_image, fb_id = check_facebook()
    if fb_message:
        send_message(fb_message, image_url=fb_image)
        state["last_fb_post"] = fb_id
        state_changed = True
        print("✅ ทำงานฝั่ง Facebook สำเร็จ")
    print("====================================")

    if state_changed:
        save_state(state)
        print("💾 บันทึกประวัติสถานะใหม่เรียบร้อย")
        
    print("🚀 DONE ALL PROCESS")

if __name__ == "__main__":
    main()
