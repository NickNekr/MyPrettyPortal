import requests

from config import app_config


def send_message(text: str) -> None:
    """
    Sends messages to telegram using the telegram bot api.
    :param text: message
    """
    url = f"{app_config.TelegramConfig.BASE_URL}sendMessage"
    bot_data = {
        "chat_id": app_config.TelegramConfig.CHAT_ID,
        "parse_mode": "HTML",
        "text": text,
    }
    response = requests.post(url, json=bot_data)
    assert response.status_code == 200
