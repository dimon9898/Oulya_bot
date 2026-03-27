import requests
from config import settings

def set_webhook():
    headers = {
        'Authorization': settings.MAX_TOKEN,
        'Content-Type': 'application/json'
    }

    payload = {
        'url': settings.WEBHOOK_URL,
        'update_types': ['message_created', 'message_callback', 'bot_started'],
        'secret': settings.SECRET_MAX
    }

    resp = requests.post('https://platform-api.max.ru/subscriptions', headers=headers, json=payload)
    print(resp.status_code, resp.text)

    return

set_webhook()