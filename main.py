import os
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- ТВОИ НАСТРОЙКИ ---
api_id = 23330271
api_hash = '4f5b104fcee7c2593eff394b19d4b67f'

# СЮДА ВПИШИ СВОЕ СЛОВО ИЗ ПРИЛОЖЕНИЯ NTFY
NTFY_TOPIC = "alarmsig"

# ID КАНАЛА, ЗА КОТОРЫМ СЛЕДИМ
source_channel_id = -1003197594249

# Берем сессию из переменных Railway
session_string = os.environ.get('SESSION_STRING')

if session_string:
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
else:
    print("ОШИБКА: Не найдена переменная SESSION_STRING!")
    exit(1)


# Функция отправки вибрации
# Исправленная функция (поддерживает русские буквы и смайлы)
def send_vibration(text):
    try:
        url = f"https://ntfy.sh/{NTFY_TOPIC}"
        
        # Мы отправляем байты, но без .encode в заголовках (requests сам справится с UTF-8 в теле)
        requests.post(url,
            data=f"📳 НОВОЕ СООБЩЕНИЕ!\n{text[:100]}".encode('utf-8'),
            headers={
                "Title": "Telegram Alarm",
                "Priority": "5",       # 5 = Максимальный (критический)
                "Tags": "call",        # <--- ГЛАВНЫЙ ТРЮК: Эмулируем входящий звонок!
                "Call": "1"            # Подтверждение для некоторых клиентов
            }
        )
        print(f"Отправлен сигнал ЗВОНКА в топик {NTFY_TOPIC}")
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")




@client.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    print("Получено новое сообщение!")
    msg_text = event.message.text or "Медиа файл"

    # Отправляем сигнал на телефон
    send_vibration(msg_text)


print("Бот-будильник запущен...")
client.start()
client.run_until_disconnected()
