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
    try:
        if register.is_registered(callback_data["telegramId"]):
            r = requests.post(url="http://localhost:8080/api/putIntoTheQueue", json=callback_data)
            return r.text.__contains__("done done done ")
    except:
        return False


# def register(data):
#     r = requests.post(url="http://localhost:8080/api/register/", json=data)
#     if r.text.__contains__(data["telegramId"]):
#         return True
#     else:
#         return False
