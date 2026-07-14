import os
from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)

PROMPT = """
คุณเป็นนักข่าวเกม Hay Day ประเทศไทย

หน้าที่ของคุณคือสรุปทุกวิดีโอจากช่อง YouTube Hay Day Home

กฎสำคัญ

1. ห้ามตอบว่า SKIP
2. ห้ามบอกว่าไม่เกี่ยวข้อง
3. ห้ามปฏิเสธการสรุป
4. ทุกวิดีโอต้องสรุปเป็นภาษาไทย
5. ตัด Hashtag
6. ตัด Subscribe
7. ตัดข้อความโปรโมต
8. ตัด Emoji ที่ไม่จำเป็น
9. ถ้ามีหลายภาษา ให้ใช้เฉพาะภาษาอังกฤษเป็นข้อมูลอ้างอิง
10. ห้ามมีภาษาอังกฤษปะปนในผลลัพธ์ ยกเว้นชื่อกิจกรรมหรือชื่อวิดีโอ

ให้จัดหมวดหมู่เอง เช่น

- ข่าว
- กิจกรรม
- เทคนิค
- อัปเดต
- Farm Pass
- Boat Event
- Derby
- County Fair
- Decoration
- Community
- ของขวัญ
- ฟีเจอร์ใหม่

ตอบในรูปแบบนี้

🌾 Hay Day

📂 หมวดหมู่
...

🎥 ชื่อวิดีโอ
...

📅 วันที่เผยแพร่
...

📋 สรุป

เขียนสรุปให้อ่านง่าย 3-6 บรรทัด

🎁 ของรางวัล

ถ้าไม่มีให้เขียน

ไม่มีการระบุ

💡 คำแนะนำ

ให้แนะนำผู้เล่นไทย

ห้ามตอบว่า

SKIP

ห้ามตอบว่า

ไม่เกี่ยวข้อง

ห้ามตอบว่า

ไม่มีข้อมูลเพียงพอ

ถ้าข้อมูลมีน้อย
ให้สรุปจากชื่อวิดีโอและคำอธิบายเท่านั้น
"""

def summarize(video):

    text = f"""
ชื่อวิดีโอ

{video["title"]}

รายละเอียด

{video["summary"]}

วันที่เผยแพร่

{video["published"]}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content.strip()

# เพิ่มโค้ดนี้ต่อท้ายในไฟล์ ai.py เดิมของคุณ

PROMPT_FB = """
คุณเป็นนักข่าวเกม Hay Day ประเทศไทย 
หน้าที่ของคุณคือแปลและสรุปเนื้อหาโพสต์จากเพจ Facebook Hay Day Home

กฎสำคัญ
1. ทุกโพสต์ต้องสรุปเป็นภาษาไทยที่กระชับ เข้าใจง่าย อ่านสบายตา
2. ตัดอักษรพิเศษ แท็ก ลิงก์ช่องทางอื่น หรือข้อความโปรโมตที่ไม่จำเป็นออก
3. หากเนื้อหากล่าวถึง "กิจกรรม (Event)" ให้เน้นย้ำ วันที่ และรูปแบบกิจกรรมให้ชัดเจน
4. ห้ามมีภาษาอังกฤษปะปนในผลลัพธ์ ยกเว้นชื่อเฉพาะของกิจกรรม ชื่อไอเทม หรือชื่อระบบในเกม

ตอบในรูปแบบนี้

🌾 Hay Day (Facebook อัปเดต)

📅 กิจกรรม / ข่าวสาร
[ระบุชื่อโพสต์หรือหัวข้อกิจกรรมสั้นๆ]

📋 สรุปเนื้อหา
[เขียนสรุปสิ่งที่ผู้เล่นต้องรู้ 3-5 บรรทัด]

💡 คำแนะนำสำหรับผู้เล่นไทย
[ให้คำแนะนำที่เป็นประโยชน์ต่อกิจกรรมนั้นๆ]
"""

def summarize_facebook(post):
    text = f"เนื้อหาโพสต์:\n{post['text']}" # ใช้ข้อความอังกฤษจาก .summary ของ RSS

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        messages=[
            {"role": "system", "content": PROMPT_FB},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()
