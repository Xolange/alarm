import os
import requests
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- НАСТРОЙКИ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'

# Топик и канал
NTFY_TOPIC = "alarmsig"
source_channel_id = -1003197594249

# Сессия
session_string = os.environ.get('SESSION_STRING')

if not session_string:
    print("❌ ОШИБКА: Нет переменной SESSION_STRING!")
    exit(1)

# --- ГЛАВНОЕ ИЗМЕНЕНИЕ: ВЕЧНОЕ ПЕРЕПОДКЛЮЧЕНИЕ ---
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,     # Бесконечные попытки (не сдаваться никогда)
    auto_reconnect=True,         # Автоматически восстанавливать связь
    retry_delay=5                # Пробовать каждые 5 секунд при разрыве
)

# Функция отправки уведомления
def send_notification(text):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=f"🔔 НОВОЕ СООБЩЕНИЕ!\n{text[:100]}".encode('utf-8'),
            headers={
                "Title": "Telegram Alarm",
                "Priority": "5",
                "Tags": "rotating_light"
            },
            timeout=5 # Таймаут 5 секунд, чтобы не виснуть на отправке
        )
        print(f"✅ Сигнал отправлен в {NTFY_TOPIC}")
    except Exception as e:
        print(f"⚠️ Ошибка отправки в ntfy: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    # Логируем ID сообщения, чтобы видеть в консоли
    print(f"📩 ПОЛУЧЕНО СООБЩЕНИЕ! ID: {event.message.id}")
    
    msg_text = event.message.text or "📷 Фото/Медиа"
    send_notification(msg_text)

print(f"🤖 Бот запущен! Слежу за каналом {source_channel_id}...")
print("🔄 Режим вечного переподключения активен.")

# Запуск
client.start()
client.run_until_disconnected()
