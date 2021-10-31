import sys

import requests
import register

from config import BASE_API_URL


def callback_to_json(data):
    separated_data = data.split(";")
    json_data = {
        "telegramId": separated_data[0],
        "subjectId": separated_data[2],
        "qplace": str(separated_data[3])
    }
    return json_data


def list_students(lesson_data: dict) -> list:
    students = []
    sorted_students = sorted(lesson_data['students'], key=lambda x: x['placeNum'])
    for student in lesson_data['students']:
        students.append(f"{student['placeNum']}. {student['studentID']['name']}\n")
    return students


def queue_json_to_add(id_data, number_in_queue, telegram_id, date, replace=str("false")):
    if register.is_registered(telegram_id):
        if number_in_queue is not None:
            json_data = {
                "telegramId": str(telegram_id),
                "subjectId": str(id_data),
                "date": str(date),
                "qplace": str(number_in_queue),
                "replace": replace
            }
        else:
            null = number_in_queue
            json_data = {
                "telegramId": str(telegram_id),
                "subjectId": str(id_data),
                "date": str(date),
                "qplace": null,
                "replace": replace
            }
        try:
            r = requests.post(url=BASE_API_URL + "putIntoTheQueue", json=json_data)
            return r.text.replace('"', '')
        except requests.exceptions:
            return ""
    else:
        return "penis"


def add_student(callback_data, telegram_id) -> str:
    print(callback_data)

    if register.is_registered(telegram_id):
        try:
            r = requests.post(url=BASE_API_URL + "putIntoTheQueue", json=callback_data)
            return r.text.replace('"', '')
        except requests.exceptions:
            return ""
