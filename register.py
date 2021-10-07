import json
import requests
from config import BASE_API_URL


def callback_to_json(callback_data: str, name, telegram_id: int):
    separated_data = callback_data.split(";")
    json_data = {
        "name": name,
        "telegramId": telegram_id,
        "subgroup": separated_data[1],
        "group": separated_data[3]
    }
    return json_data


def is_registered(telegram_id):
    r = requests.get(url=f"{BASE_API_URL}isRegistered/{telegram_id}")
    response = r.text
    if response == "true":
        return True
    else:
        return False


def register(callback_data: str, name, telegram_id: int):
    json_data = callback_to_json(callback_data, name, telegram_id)
    try:
        r = requests.post(url=BASE_API_URL + "register/", json=json_data)
        return r.text.replace('"', '')
    except requests.exceptions:
        return ""
