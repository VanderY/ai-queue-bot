import sys

import requests
import register


def callback_to_json(data):
    separated_data = data.split(";")
    json_data = {
        "telegramId": separated_data[0],
        "subject": separated_data[2],
        "date": separated_data[5],
        "qPlace": "1"
    }
    return json_data


def add_student(callback_data):
    print(callback_data)
    if register.is_registered(callback_data["telegramId"]):
        r = requests.post(url="https://chix-pix.com/api/putIntoTheQueue", json=callback_data)

        print(r.text)
        return r.text.__contains__("done done done ")
    return False
