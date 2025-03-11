from celery import shared_task
import requests
import os
from dotenv import load_dotenv

load_dotenv()

@shared_task
def send_telegram_message(user_id, message):
    """Отправляет сообщение в Telegram через бота. Нужен токен для его работы"""
    bot_token = os.getenv("BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": message
    }
    requests.post(url, json=payload)