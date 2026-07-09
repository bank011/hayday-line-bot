from groq import Groq
import os

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)


def summarize(text):

    prompt = f"""
คุณคือผู้เชี่ยวชาญเกม Hay Day

อ่านข้อความต่อไปนี้ แล้วตอบเป็นภาษาไทย

จัดรูปแบบดังนี้

🌾 ชื่อกิจกรรม

📅 วันที่

🎁 ของรางวัล

📋 สรุป

💡 คำแนะนำ

ข้อความ

{text}

ห้ามตอบเป็นภาษาอังกฤษ
"""

    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return chat.choices[0].message.content
