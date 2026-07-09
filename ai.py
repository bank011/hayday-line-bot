import os
from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)


PROMPT = """
คุณคือผู้เชี่ยวชาญเกม Hay Day

อ่านข่าวแล้วตอบเป็นภาษาไทย

ถ้าข่าวไม่เกี่ยวกับ

- Event
- Update
- Maintenance
- Farm Pass
- Derby
- Valley
- Double Coin
- Double XP
- Gift
- Decoration
- Collaboration

ให้ตอบ

SKIP

======================

ถ้าใช่ ให้ตอบรูปแบบนี้

🌾 Hay Day

📢 ประเภท
...

📅 วันที่
...

🎁 ของรางวัล
...

📋 สรุป
...

💡 คำแนะนำ
...

ตอบเป็นภาษาไทยทั้งหมด
"""


def summarize(article):

    text = f"""

หัวข้อ

{article['title']}

เนื้อหา

{article['content']}

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
