import requests
import os

# ดึงค่า API Key ที่เราจะไปเซฟไว้ใน GitHub Secrets
MPW_API_KEY = os.environ.get("MPW_API_KEY", "")

def send_message(text):
    if not MPW_API_KEY:
        print("❌ LINE ERROR: ไม่พบรหัส MPW_API_KEY ในระบบ Secrets")
        return

    # ลิงก์ API ของระบบ MPW Line Auto
    url = "https://mpw-lineauto.com/api/v1/notify"
    
    headers = {
        "Authorization": f"Bearer {MPW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # ข้อความที่จะส่งเข้าไลน์กลุ่ม
    payload = {
        "message": text
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if r.status_code == 200:
            print("✅ LINE SUCCESS: ส่งข่าวสารเข้ากลุ่มไลน์สำเร็จ (ผ่าน MPW)")
        else:
            print(f"❌ LINE ERROR: รหัสข้อผิดพลาด {r.status_code}")
            print(r.text)
            r.raise_for_status()
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ API: {e}")
