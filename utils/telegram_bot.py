# utils/telegram_bot.py

import requests
import toml

def send_telegram_message(message):
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        bot_token = secrets["telegram"]["bot_token"]
        chat_id = "@stafxsignals"  # Your public channel

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Message sent successfully.")
        return True

    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return False
