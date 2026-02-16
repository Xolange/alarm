import os
import aiohttp
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- НАСТРОЙКИ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'

# Топик (Убедись, что он совпадает с телефоном!)
NTFY_TOPIC = "alarmsig"
source_channel_id = -1003197594249

# Сессия
session_string = os.environ.get('SESSION_STRING')
if not session_string:
    print("❌ ОШИБКА: Нет переменной SESSION_STRING!")
    exit(1)

# Клиент (Вечное соединение)
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,
    auto_reconnect=True,
    retry_delay=5
)

# Функция отправки (Асинхронная + ЗВОНОК)
async def send_critical_alert(text):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    # Формируем "Злой" запрос
    headers = {
        "Title": "Telegram Call",
        "Priority": "5",       # Максимальный (пробивает тишину)
        "Tags": "call",        # <--- ГЛАВНОЕ: Эмуляция звонка (долгая вибрация)
        "Call": "1"            # Подтверждение для Android/iOS
    }
    
    try:
        # Используем aiohttp сессию (она супер-быстрая)
        async with aiohttp.ClientSession() as session:
            await session.post(
                url,
                data=f"📳 ВХОДЯЩИЙ СИГНАЛ!\n{text[:50]}".encode('utf-8'),
                headers=headers,
                timeout=5
            )
        print(f"✅ Звонок отправлен: {text[:20]}...")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    # Логируем сразу
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    msg_text = event.message.text or "Файл"
    
    # Запускаем отправку в фоне. Бот МГНОВЕННО готов к следующему сообщению.
    asyncio.create_task(send_critical_alert(msg_text))

print(f"🤖 Бот запущен! Топик: {NTFY_TOPIC}")
client.start()
client.run_until_disconnected()
