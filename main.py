import os
import aiohttp
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from datetime import datetime

# --- НАСТРОЙКИ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'
NTFY_TOPIC = "alarmsig"
source_channel_id = -1003197594249

# Сессия
session_string = os.environ.get('SESSION_STRING')
if not session_string:
    print("❌ ОШИБКА: Нет переменной SESSION_STRING!")
    exit(1)

# Клиент (с защитой от засыпания)
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,
    auto_reconnect=True,
    retry_delay=5
)

# Функция отправки (НАДЕЖНАЯ ВЕРСИЯ)
async def send_notification(text):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                url,
                data=f"🚨 ВАЖНО!\n{text[:100]}".encode('utf-8'),
                headers={
                    "Title": "Telegram Alarm",
                    "Priority": "5",       # Максимальный приоритет (работало хорошо)
                    "Tags": "rotating_light" # Сирена (работало хорошо)
                },
                timeout=10
            )
        print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Уведомление отправлено!")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")

# Пинг, чтобы бот не спал
async def keep_alive():
    while True:
        try:
            me = await client.get_me()
            # print(f"💓 Пинг...") # Можно раскомментировать для отладки
        except Exception as e:
            print(f"⚠️ Потеря связи с Telegram: {e}")
        await asyncio.sleep(60)

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    print(f"📩 [{datetime.now().strftime('%H:%M:%S')}] НОВОЕ СООБЩЕНИЕ! ID: {event.message.id}")
    msg_text = event.message.text or "Файл/Фото"
    
    # Отправляем мгновенно в фоне
    asyncio.create_task(send_notification(msg_text))

print(f"🤖 Бот запущен! Топик: {NTFY_TOPIC}")
client.start()

# Запускаем пинг параллельно
loop = asyncio.get_event_loop()
loop.create_task(keep_alive())

client.run_until_disconnected()
