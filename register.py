import json
import requests
from config import BASE_API_URL


def callback_to_json(data):
    separated_data = data.split(";")
    json_data = {
        "name": separated_data[4],
        "telegramId": separated_data[5],
        "subgroup": separated_data[1],
        "group": separated_data[3]
    }
    return json_data


def is_registered(telegramId):
    r = requests.get(url=f"{BASE_API_URL}isRegistered/{telegramId}")
    response = r.text
    if response == "true":
        return True
    else:
        return False


def register(data):
    r = requests.post(url=BASE_API_URL + "register/", json=data)
    if r.text.__contains__(data["telegramId"]):
        return True
    else:
        return False
