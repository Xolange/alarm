import os
import requests
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- ТВОИ НАСТРОЙКИ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'

# ВСТАВЬ СЮДА СВОЙ ТОПИК
NTFY_TOPIC = "ВСТАВЬ_ТУТ_СВОЙ_ТОПИК"  

# ID КАНАЛА
source_channel_id = -1003507320916

# Сессия
session_string = os.environ.get('SESSION_STRING')

if not session_string:
    print("ОШИБКА: Нет переменной SESSION_STRING!")
    exit(1)

# СОЗДАЕМ КЛИЕНТ С АВТО-ПЕРЕПОДКЛЮЧЕНИЕМ
client = TelegramClient(
    StringSession(session_string),
    api_id, 
    api_hash,
    connection_retries=None,     # Бесконечные попытки переподключения
    retry_delay=5                # Пробовать каждые 5 секунд
)

# Функция отправки "ЗВОНКА" (Долгая вибрация)
def send_vibration(text):
    try:
        url = f"https://ntfy.sh/{NTFY_TOPIC}"
        requests.post(url,
            data=f"📳 ЗВОНОК!\n{text[:100]}".encode('utf-8'),
            headers={
                "Title": "Telegram Call",
                "Priority": "5",       # Максимальный
                "Tags": "call",        # Эмуляция звонка для долгой вибрации
                "Call": "1"
            }
        )
        print(f"Сигнал отправлен в {NTFY_TOPIC}")
    except Exception as e:
        print(f"Ошибка уведомления: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    print(f"Поймал сообщение! ID: {event.message.id}")
    msg_text = event.message.text or "Медиа"
    send_vibration(msg_text)

print("Бот запущен и держит соединение...")

# Запускаем клиент
client.start()
client.run_until_disconnected()
