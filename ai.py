import os
from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)


def summarize(article):

    prompt = f"""
คุณคือผู้เชี่ยวชาญเกม Hay Day

อ่านข่าวนี้ แล้วตอบเป็นภาษาไทยเท่านั้น

ถ้าไม่ใช่ข่าวเกี่ยวกับ

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

ให้ตอบเพียง

SKIP

======================

ถ้าใช่ ให้ตอบตามรูปแบบนี้

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

======================

หัวข้อ
{article["title"]}

วันที่
{article["date"]}

เนื้อหา
{article["content"]}

"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
