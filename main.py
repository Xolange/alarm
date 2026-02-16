import os
import requests
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- НАСТРОЙКИ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'
NTFY_TOPIC = "alarmsig"  # <--- ПРОВЕРЬ, ЧТО В ПРИЛОЖЕНИИ ТОЧНО ТАК ЖЕ
source_channel_id = -1003197594249

# Сессия
session_string = os.environ.get('SESSION_STRING')
if not session_string:
    print("❌ ОШИБКА: Нет переменной SESSION_STRING!")
    exit(1)

client = TelegramClient(StringSession(session_string), api_id, api_hash, connection_retries=None, auto_reconnect=True, retry_delay=5)

def send_debug_notification(text):
    try:
        url = f"https://ntfy.sh/{NTFY_TOPIC}"
        
        # Отправляем ПРОСТОЕ уведомление (без звонков и фокусов), чтобы проверить связь
        response = requests.post(
            url,
            data=f"🔔 ТЕСТ СВЯЗИ! {text[:30]}".encode('utf-8'),
            headers={
                "Title": "Debug Message",
                "Priority": "5",
                "Tags": "warning"
            },
            timeout=10
        )
        
        # ВЫВОДИМ ОТВЕТ СЕРВЕРА (ЭТО САМОЕ ВАЖНОЕ!)
        print(f"📡 Статус ответа: {response.status_code}")
        print(f"📝 Текст ответа: {response.text}")
        
    except Exception as e:
        print(f"⚠️ Ошибка запроса: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    print(f"📩 ПОЛУЧЕНО! ID: {event.message.id}")
    msg_text = event.message.text or "Файл"
    threading.Thread(target=send_debug_notification, args=(msg_text,)).start()

print(f"🤖 Бот-Debug запущен! Топик: {NTFY_TOPIC}")
client.start()
client.run_until_disconnected()
