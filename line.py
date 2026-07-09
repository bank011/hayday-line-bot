import requests

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_GROUP_ID


def send_message(news):

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "to": LINE_GROUP_ID,
        "messages": [
            {
                "type": "flex",
                "altText": news["title"],
                "contents": {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": "https://hayday.com/static/images/share.jpg",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎮 Hay Day News",
                                "weight": "bold",
                                "size": "xl"
                            },
                            {
                                "type": "text",
                                "text": news["source"],
                                "size": "sm",
                                "color": "#888888",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": news["title"],
                                "wrap": True,
                                "margin": "lg",
                                "size": "md"
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "action": {
                                    "type": "uri",
                                    "label": "📖 อ่านข่าว",
                                    "uri": news["link"]
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }

    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=payload,
    )

    print(r.status_code)
    print(r.text)
