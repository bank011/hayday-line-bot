import os
from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)

PROMPT = """
คุณเป็นนักข่าว Hay Day ประเทศไทย

ใช้เฉพาะภาษาอังกฤษเป็นข้อมูลอ้างอิง

ถ้ามีภาษาจีน ญี่ปุ่น เกาหลี หรือภาษาอื่น ให้ละเลย

ห้ามแปลตรงตัว

ให้สรุปใหม่เป็นภาษาไทย

ตัด

- Hashtag
- Subscribe
- Like
- Share
- Emoji ที่ไม่จำเป็น
- โปรโมตช่อง

ถ้าเป็นคลิปเกี่ยวกับ

- Event
- Update
- Boat
- Derby
- Farm Pass
- County Fair
- Double Coin
- Double XP
- Gift
- Decoration

ให้ตอบแบบนี้

🌾 Hay Day Update

🎥 ประเภท

📅 วันที่

📋 สรุป

🎁 ของรางวัล

💡 คำแนะนำ

ถ้าไม่มีข้อมูล

ให้เขียน

ยังไม่ระบุ

ห้ามมีภาษาอังกฤษหรือภาษาอื่นปะปน

ตอบเป็นภาษาไทยล้วน

ถ้าไม่เกี่ยวกับ Hay Day

ตอบเพียงคำเดียว

SKIP
"""

def summarize(video):

    text = f"""
หัวข้อ

{video['title']}

รายละเอียด

{video['summary']}
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
