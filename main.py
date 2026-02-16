import os
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- ТВОИ ДАННЫЕ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'

# ТВОЙ ТОПИК ДЛЯ УВЕДОМЛЕНИЙ
NTFY_TOPIC = "alarmsig"

# ТВОЙ НОВЫЙ КАНАЛ (ОТКУДА ЖДЕМ СООБЩЕНИЯ)
source_channel_id = -1003197594249

# Берем сессию из переменных Railway
session_string = os.environ.get('SESSION_STRING')

if not session_string:
    print("ОШИБКА: Нет переменной SESSION_STRING в настройках Railway!")
    exit(1)

# Создаем клиент с защитой от разрывов связи
client = TelegramClient(
    StringSession(session_string),
    api_id,
    api_hash,
    connection_retries=None,     # Пытаться подключиться бесконечно
    retry_delay=5                # Каждые 5 секунд
)

# Функция для ДОЛГОЙ вибрации (как при звонке)
def send_long_vibration(text):
    try:
        url = f"https://ntfy.sh/{NTFY_TOPIC}"
        
        # Отправляем запрос с эмуляцией звонка
        requests.post(url,
            data=f"🔔 НОВОЕ СООБЩЕНИЕ!\n{text[:100]}".encode('utf-8'),
            headers={
                "Title": "Telegram Alarm",   # Заголовок
                "Priority": "5",             # Максимальный приоритет (5)
                "Tags": "call",              # <--- ЭТО ВАЖНО! Делает долгую вибрацию/звонок
                "Call": "1"                  # Подтверждение звонка для Android/iOS
            }
        )
        print(f"✅ Сигнал ЗВОНКА отправлен в топик {NTFY_TOPIC}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")

@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    print(f"📩 Пришло сообщение! ID: {event.message.id}")
    
    # Текст сообщения (или заглушка, если только фото)
    msg_text = event.message.text or "📷 Фото/Медиа"
    
    # Отправляем сигнал на телефон
    send_long_vibration(msg_text)

print(f"🤖 Бот запущен и следит за каналом {source_channel_id}...")
print(f"📡 Уведомления уходят в топик: {NTFY_TOPIC}")

# Запуск клиента
client.start()
client.run_until_disconnected()
