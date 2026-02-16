import os
import aiohttp
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

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

# Клиент (Встроенная защита от разрывов)
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,  # Бесконечные попытки подключения
    auto_reconnect=True,      # Авто-реконнект (встроенный)
    retry_delay=3             # Быстрый повтор при разрыве
)

# Функция отправки (Простая и надежная)
async def send_alert(text):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    try:
        # Используем быстрый aiohttp
        async with aiohttp.ClientSession() as session:
            await session.post(
                url,
                data=f"🚨 ВАЖНО!\n{text[:100]}".encode('utf-8'),
                headers={
                    "Title": "Telegram Alarm",
                    "Priority": "5",       # 5 = Максимальный (работает лучше всего)
                    "Tags": "rotating_light"
                },
                timeout=10
            )
        print(f"✅ Уведомление отправлено!")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    # Логируем
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    msg_text = event.message.text or "Файл/Фото"
    
    # Отправляем мгновенно в фоне
    asyncio.create_task(send_alert(msg_text))

print(f"🤖 Бот запущен! Топик: {NTFY_TOPIC}")

# ЗАПУСК (Стандартный метод Telethon)
client.start()
client.run_until_disconnected()
