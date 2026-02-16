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

client = TelegramClient(StringSession(session_string), api_id, api_hash, connection_retries=None, auto_reconnect=True, retry_delay=5)

def send_silent_call(text):
    try:
        url = f"https://ntfy.sh/{NTFY_TOPIC}"
        
        requests.post(
            url,
            data=f"📳 Входящий сигнал!\n{text[:50]}".encode('utf-8'),
            headers={
                "Title": "Telegram Call",
                "Priority": "4",       # <--- ИСПРАВИЛ НА 4. Теперь он будет молчать в беззвучном!
                "Tags": "call",        # Эмуляция звонка (чтобы вибрировало долго)
                "Call": "1"
            },
            timeout=10
        )
        print("✅ Сигнал отправлен (Priority 4)")
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    msg_text = event.message.text or "Файл"
    threading.Thread(target=send_silent_call, args=(msg_text,)).start()

print(f"🤖 Бот запущен! Топик: {NTFY_TOPIC}")
client.start()
client.run_until_disconnected()
