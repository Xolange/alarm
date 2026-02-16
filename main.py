import os
import aiohttp # <--- Асинхронные запросы (быстро и не блокирует)
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- НАСТРОЙКИ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'
NTFY_TOPIC = "alarmsig"  # Вернем старый топик, если хочешь, или новый
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

# Асинхронная функция отправки
async def send_async_notification(text):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    # Используем aiohttp вместо requests
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                url,
                data=f"🔔 НОВОЕ СООБЩЕНИЕ!\n{text[:50]}".encode('utf-8'),
                headers={
                    "Title": "Telegram",
                    "Priority": "5",       # 5 = Пробивает режимы
                    "Tags": "rotating_light"
                },
                timeout=10
            )
        print(f"✅ Сигнал отправлен: {text[:20]}...")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    # Сразу пишем в лог
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    msg_text = event.message.text or "Файл"
    
    # Запускаем отправку как фоновую задачу (Fire-and-forget)
    # Бот НЕ ЖДЕТ ответа от сервера и сразу готов к новому сообщению
    asyncio.create_task(send_async_notification(msg_text))

print(f"🤖 Бот запущен! Топик: {NTFY_TOPIC}")
client.start()
client.run_until_disconnected()
