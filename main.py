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

# Сессия из Railway
session_string = os.environ.get('SESSION_STRING')

if not session_string:
    print("❌ ОШИБКА: Нет переменной SESSION_STRING!")
    exit(1)

# Клиент (с защитой от разрывов связи)
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,
    auto_reconnect=True,
    retry_delay=5
)

# Функция отправки (АСИНХРОННАЯ + ЗВОНОК)
async def send_call_signal():
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    # Запускаем в фоне, чтобы бот не ждал ответа
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: requests.post(
        url,
        data="📳 НОВОЕ СООБЩЕНИЕ!".encode('utf-8'),
        headers={
            "Title": "Telegram Call",
            "Priority": "5",       # Максимальный
            "Tags": "call",        # <--- ВЕРНУЛИ ЗВОНОК (Жесткая вибрация)
            "Call": "1"            # Подтверждение звонка
        },
        timeout=5
    ))
    print("✅ Сигнал ЗВОНКА отправлен (фон)")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    # Сразу пишем в лог
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    
    # Запускаем отправку звонка параллельно
    # Бот сразу освобождается для следующего сообщения
    asyncio.create_task(send_call_signal())

print(f"🤖 Бот запущен! Режим: ЗВОНОК (Асинхронно)")
client.start()
client.run_until_disconnected()
