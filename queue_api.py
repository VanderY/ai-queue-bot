import sys

import requests
import register

from config import BASE_API_URL


def callback_to_json(data):
    separated_data = data.split(";")
    json_data = {
        "telegramId": separated_data[0],
        "subject": separated_data[2],
        "date": separated_data[5],
        "qplace": str(separated_data[6])
    }
    return json_data


def add_student(callback_data) -> str:
    print(callback_data)
    if register.is_registered(callback_data["telegramId"]):
        try:
            r = requests.post(url=BASE_API_URL + "putIntoTheQueue", json=callback_data)
            return r.text.replace('"', '')
        except requests.exceptions:
            return ""
