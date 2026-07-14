import requests
import os

# ดึงค่า API Key จากระบบ Secrets
MPW_API_KEY = os.environ.get("MPW_API_KEY", "")

def get_line_account_id():
    """ฟังก์ชันดึง line_account_id อัตโนมัติจากชื่อบัญชีใหม่"""
    url = "https://mpw-lineauto.com/api/v1/line-accounts"
    headers = {
        "X-API-Key": MPW_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            res_data = r.json()
            if res_data.get("success") and "data" in res_data:
                # ค้นหาบัญชีที่ชื่อตรงกับ "ผู้ใหญ่บ้าน วังเวงฟาร์ม"
                for account in res_data["data"]:
                    if account.get("name") == "ผู้ใหญ่บ้าน วังเวงฟาร์ม":
                        print(f"🔍 พบ LINE Account ID ของผู้ใหญ่บ้าน: {account.get('id')}")
                        return account.get("id")
                
                if len(res_data["data"]) > 0:
                    return res_data["data"][0].get("id")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงเส้นบัญชี: {e}")
    return None

def send_message(text, image_url=None):
    if not MPW_API_KEY:
        print("❌ LINE ERROR: ไม่พบรหัส MPW_API_KEY ในระบบ Secrets")
        return

    line_account_id = get_line_account_id()
    if not line_account_id:
        print("❌ LINE ERROR: ไม่สามารถระบุ line_account_id ได้ ระบบข้ามการส่ง")
        return

    url = "https://mpw-lineauto.com/api/v1/send"
    
    headers = {
        "X-API-Key": MPW_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "line_account_id": int(line_account_id),
        "search_terms": ["วังเวง ฟาร์ม"],
        "message": text
    }

    # แนบลิงก์รูปภาพเพิ่มเข้าไปในระบบของ MPW ถ้ามีส่งมา
    if image_url:
        payload["image_url"] = image_url

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            print("✅ LINE SUCCESS: ผู้ใหญ่บ้านส่งข้อความพร้อมรูปภาพเข้ากลุ่มสำเร็จ!")
        else:
            print(f"❌ LINE ERROR: รหัสข้อผิดพลาด {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ API ส่งข้อความ: {e}")
