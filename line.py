import requests
import os

# ดึงค่า API Key จากระบบ Secrets
MPW_API_KEY = os.environ.get("MPW_API_KEY", "")

def get_line_account_id():
    """ฟังก์ชันดึง line_account_id อัตโนมัติจากชื่อบัญชี"""
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
                # ค้นหาบัญชีที่ชื่อตรงกับ "Hay Day Admin"
                for account in res_data["data"]:
                    if account.get("name") == "Hay Day Admin":
                        print(f"🔍 พบ LINE Account ID อัตโนมัติ: {account.get('id')}")
                        return account.get("id")
                
                # ถ้าไม่เจอชื่อที่ตรงกัน ให้ดึง ID ของบัญชีแรกในระบบมาใช้ก่อน
                if len(res_data["data"]) > 0:
                    fallback_id = res_data["data"][0].get("id")
                    print(f"⚠️ ไม่พบชื่อ Hay Day Admin ใช้ ID แรกในระบบแทน: {fallback_id}")
                    return fallback_id
        print(f"❌ ดึงข้อมูลบัญชีไม่สำเร็จ (Status: {r.status_code})")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงดึงเส้นบัญชี: {e}")
    return None

def send_message(text):
    if not MPW_API_KEY:
        print("❌ LINE ERROR: ไม่พบรหัส MPW_API_KEY ในระบบ Secrets")
        return

    # เรียกหา ID บัญชีแบบอัตโนมัติ
    line_account_id = get_line_account_id()
    if not line_account_id:
        print("❌ LINE ERROR: ไม่สามารถระบุ line_account_id ได้ ระบบข้ามการส่ง")
        return

    # ลิงก์ปลายทางสำหรับส่งข้อความ
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

    try:
        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if r.status_code == 200:
            print("✅ LINE SUCCESS: ส่งข่าวสารเข้ากลุ่มไลน์สำเร็จแล้ว!")
        else:
            print(f"❌ LINE ERROR: รหัสข้อผิดพลาด {r.status_code}")
            print(r.text)
            r.raise_for_status()
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ API ส่งข้อความ: {e}")
