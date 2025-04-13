
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Загрузка токенов из .env файла
load_dotenv()

YC_TOKEN = os.getenv('YC_TOKEN')
USER_TOKEN = os.getenv('USER_TOKEN')
PARTNER_TOKEN = os.getenv('PARTNER_TOKEN')
CRM_TOKEN = os.getenv('CRM_TOKEN')

app = Flask(__name__)
CORS(app)

headers = {
    "Accept": "application/vnd.yclients.v2+json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {PARTNER_TOKEN}, User {USER_TOKEN}"
}

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TG_CHAT_ID, 'text': text}
    try:
        r = requests.post(url, json=payload)
        print(f"📨 Сообщение в Telegram отправлено (код {r.status_code})")
    except Exception as e:
        print(f"⚠️ Ошибка отправки в Telegram: {e}")

def get_calls():
    url = "https://api.yclients.com/api/v1/voip/calls"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Получены данные о звонках:")
            calls_data = response.json()
            print(json.dumps(calls_data, indent=2, ensure_ascii=False))
            return calls_data
        else:
            print(f"❌ Ошибка: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    print("🔍 Получен запрос на /webhook")
    try:
        data = request.get_json()
        if data:
            print("📥 Данные запроса:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("❌ Не удалось распарсить JSON из запроса.")
    except Exception as e:
        print(f"❌ Ошибка при обработке запроса: {e}")
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    caller_info = data.get("caller_id_number", "Неизвестный номер")
    direction = data.get("direction", "неизвестное направление")
    call_status = data.get("event", "неизвестное событие")

    message = (
        f"📞 Новый звонок!
"
        f"👤 Номер: {caller_info}
"
        f"➡️ Направление: {direction}
"
        f"📍 Событие: {call_status}"
    )

    send_telegram_message(message)
    return jsonify({"status": "success"}), 200

def setup_integration():
    payload = {
        "command": "setup",
        "type": "enable",
        "crm_token": CRM_TOKEN
    }

    print("📡 Отправка запроса на включение интеграции...")
    try:
        response = requests.post("https://api.yclients.com/api/v1/voip/integration", headers=headers, data=json.dumps(payload))
        if response.status_code == 202:
            print("✅ Интеграция подключена успешно!")
        else:
            print("❌ Ошибка подключения:")
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при подключении: {e}")

if __name__ == '__main__':
    setup_integration()
    print("🟢 Запуск Flask-сервера на порту 5050...")
    app.run(debug=True, port=5050)
