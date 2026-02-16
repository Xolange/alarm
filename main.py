import os
import requests
import threading
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

# Клиент
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,
    auto_reconnect=True,
    retry_delay=5
)

# Функция отправки (В отдельном потоке, чтобы не тормозить)
def send_push_background():
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data="📳 ЗВОНОК! НОВОЕ СООБЩЕНИЕ!".encode('utf-8'),
            headers={
                "Title": "Telegram Alert",
                "Priority": "5",
                "Tags": "call",      # Эмуляция звонка (долгая вибрация)
                "Call": "1"
            },
            timeout=10
        )
        print("✅ Сигнал отправлен!")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    
    # Запускаем отправку в фоновом потоке (самый надежный способ)
    # Это гарантирует, что бот сразу готов к следующему сообщению
    threading.Thread(target=send_push_background).start()

print(f"🤖 Бот запущен! Слежу за каналом {source_channel_id}...")
client.start()
client.run_until_disconnected()
