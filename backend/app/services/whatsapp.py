import requests
from ..config import settings

def send_text(to_number: str, text: str):
    url = f"https://graph.facebook.com/v20.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()
