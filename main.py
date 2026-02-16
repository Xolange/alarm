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

# Клиент
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,
    auto_reconnect=True,
    retry_delay=5
)

# Функция отправки (теперь работает в фоне и не вешает бота)
async def send_notification_async(text):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: requests.post(
            url,
            data=f"🔔 НОВОЕ СООБЩЕНИЕ!\n{text[:100]}".encode('utf-8'),
            headers={
                "Title": "Telegram Alarm",
                "Priority": "5",       # <--- ВЕРНУЛИ 5 (MAX). Самый важный уровень.
                "Tags": "rotating_light" # Значок мигалки
            },
            timeout=5
        ))
        print(f"✅ ЖЕСТКИЙ Сигнал отправлен: {text[:20]}...")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")


@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    # Сразу пишем в лог, что сообщение пришло
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    
    msg_text = event.message.text or "📷 Фото/Медиа"
    
    # Запускаем отправку уведомления "параллельно"
    # Бот сразу готов принимать следующее сообщение
    asyncio.create_task(send_notification_async(msg_text))

print(f"🤖 Бот запущен! Слежу за каналом {source_channel_id}...")
client.start()
client.run_until_disconnected()
