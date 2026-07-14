import os
import json
import google.generativeai as genai
import feedparser
import requests
from bs4 import BeautifulSoup
from line import send_message

# ตั้งค่า Google Gemini AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

# ชื่อไฟล์สำหรับบันทึกประวัติการส่งป้องกันส่งซ้ำ
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

def ask_gemini(prompt):
    """ฟังก์ชันให้ Gemini ช่วยแปลและสรุปเนื้อหาเป็นภาษาไทย"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

def check_youtube():
    """ตรวจสอบวิดีโอใหม่จาก YouTube ช่อง Hay Day และส่งข้อความพร้อมรูปภาพ"""
    print("📺 Checking YouTube...")
    # RSS Feed ของช่อง Hay Day Official
    channel_id = "UC6qZ8kWG0KstK-V6d74E8rw"
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        print("❌ ไม่สามารถดึงข้อมูล YouTube RSS ได้")
        return None, None

    latest_entry = feed.entries[0]
    video_id = latest_entry.yt_videoid
    video_title = latest_entry.title
    video_url = latest_entry.link

    # 📸 ดึงลิงก์รูปหน้าปกวิดีโอ YouTube แบบความละเอียดสูง
    video_thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    state = load_state()
    if state.get("last_video") == video_id:
        print("⏭️ YouTube: ไม่มีวิดีโอใหม่ (ส่งไปแล้ว)")
        return None, None

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
    
    summary = ask_gemini(prompt)
    if not summary:
        summary = f"🌾 Hay Day (YouTube อัปเดต)\n📺 วิดีโอใหม่: {video_title}"

    message = f"{summary}\n\n🔗 รับชมวิดีโอฉบับเต็ม:\n{video_url}\n\n🤖 Powered by Hay Day AI News Bot"
    
    return message, video_thumbnail, video_id

def check_facebook():
    """ตรวจสอบโพสต์ใหม่จากเพจ Facebook Hay Day และส่งข้อความพร้อมรูปภาพ"""
    print("📖 Checking Facebook...")
    page_url = "https://m.facebook.com/haydayhome1/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }
    
    try:
        r = requests.get(page_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # ค้นหาโพสต์ล่าสุด
        post_element = soup.find('div', {'data-ft': True})
        if not post_element:
            print("❌ ไม่พบโพสต์บนหน้า Facebook Page")
            return None, None

        # แกะ ID โพสต์
        try:
            ft_data = json.loads(post_element['data-ft'])
            post_id = ft_data.get('top_level_post_id')
        except:
            post_id = str(hash(post_element.text))

        state = load_state()
        if state.get("last_fb_post") == post_id:
            print("⏭️ Facebook: ไม่มีโพสต์ใหม่ (ส่งไปแล้ว)")
            return None, None

        # แกะเนื้อหาข้อความ
        post_text = post_element.text.strip()
        
        # 📸 ค้นหาลิงก์รูปภาพประกอบโพสต์
        fb_image = None
        img_tag = post_element.find('img')
        if img_tag and img_tag.get('src'):
            fb_image = img_tag['src']

        print(f"🆕 พบโพสต์ Facebook ใหม่ ID: {post_id}")
        
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
        
        summary = ask_gemini(prompt)
        if not summary:
            summary = f"🌾 Hay Day (Facebook อัปเดต)\n📢 โพสต์ใหม่: {post_text[:200]}..."

        post_link = f"https://m.facebook.com/story.php?story_fbid={post_id}&id=haydayhome1"
        message = f"{summary}\n\n🔗 ลิงก์โพสต์ต้นฉบับ:\n{post_link}\n\n🤖 Powered by Hay Day AI News Bot"
        
        return message, fb_image, post_id
        
    except Exception as e:
        print(f"❌ Facebook Scraping Error: {e}")
        return None, None

def main():
    print("====================================")
    print("🐔 Hay Day Home Bot (YouTube & Facebook)")
    print("====================================")
    
    state = load_state()
    state_changed = False

    # 1. รันระบบตรวจสอบ YouTube
    yt_message, yt_image, yt_id = check_youtube()
    if yt_message:
        # 🚀 ส่งข้อความพร้อมรูปภาพเข้าไลน์กลุ่ม
        send_message(yt_message, image_url=yt_image)
        state["last_video"] = yt_id
        state_changed = True
        print("✅ ทำงานฝั่ง YouTube สำเร็จ")
    print("------------------------------------")

    # 2. รันระบบตรวจสอบ Facebook
    fb_message, fb_image, fb_id = check_facebook()
    if fb_message:
        # 🚀 ส่งข้อความพร้อมรูปภาพเข้าไลน์กลุ่ม
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
