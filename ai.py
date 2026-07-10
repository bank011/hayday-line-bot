import os
from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)

PROMPT = """
คุณคือผู้เชี่ยวชาญเกม Hay Day

อ่านข้อความจาก YouTube

หน้าที่ของคุณคือ

1. แปลเป็นภาษาไทย
2. สรุปให้อ่านง่าย
3. ถ้าเป็นกิจกรรมให้บอก
- วันเริ่ม
- วันสิ้นสุด
- ของรางวัล
- คำแนะนำ

ถ้าไม่เกี่ยวกับเกม Hay Day

ตอบ

SKIP

ตอบเป็นภาษาไทยทั้งหมด
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
