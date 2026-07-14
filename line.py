import requests
import os

# ดึงค่า API Key จากระบบ Secrets
MPW_API_KEY = os.environ.get("MPW_API_KEY", "")

def send_message(text):
    if not MPW_API_KEY:
        print("❌ LINE ERROR: ไม่พบรหัส MPW_API_KEY ในระบบ Secrets")
        return

    # ลิงก์ปลายทางที่ถูกต้องตามเอกสาร API ของเว็บ
    url = "https://mpw-lineauto.com/api/v1/send"
    
    headers = {
        "X-API-Key": MPW_API_KEY,
        "Content-Type": "application/json"
    }
    
    # โครงสร้าง Data ที่ระบุทั้งชื่อบัญชีและอีเมลเพื่อความแม่นยำ
    payload = {
        "line_account": "Hay Day Admin",
        "line_username": "thaimixdj@gmail.com",
        "search_terms": ["วังเวง ฟาร์ม"],
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
            print("✅ LINE SUCCESS: ส่งข่าวสารเข้าคิวรอส่งในกลุ่มไลน์สำเร็จ")
        else:
            print(f"❌ LINE ERROR: รหัสข้อผิดพลาด {r.status_code}")
            print(r.text)
            r.raise_for_status()
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ API: {e}")
