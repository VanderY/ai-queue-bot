import sys

import requests
from aiogram import types

import api_queue_parser
import keyboards
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


async def status_code_handler(status_code, state, lesson_id: str, lesson_name: str, lesson_time: str, number_in_queue: int = None):
    message = types.Message()
    if status_code == "ACCEPTED":
        queue = api_queue_parser.get_queue_by_id(lesson_id)
        students = ""
        for student in queue:
            students += f"{student}\n"
        message = types.Message(text=f'Очередь на {lesson_name}'
                                     f' {lesson_time}:\n'
                                     f'{students}')
        await state.reset_state()
        return message
    elif status_code == "CONFLICT":
        keyboard = keyboards.yes_no_keyboard(number_in_queue)
        if number_in_queue is not None:
            message = types.Message(text=f'Вы уже записаны в очередь на {lesson_name}'
                                         f' {lesson_time}, '
                                         f'хотите перезаписаться?',
                                    reply_markup=keyboard)
        else:
            message = types.Message(text=f'Вы уже записаны в очередь на {lesson_name}'
                                         f' {lesson_time}, '
                                         f'хотите перезаписаться на ближайшее место?',
                                    reply_markup=keyboard)
        return message
    elif status_code == "BAD_REQUEST":
        message = types.Message(text=f'Введите корректное значение')
        return message
    elif status_code == "BAD_GATEWAY":
        message = types.Message(text=f'Вы пытаетесь записаться не в свою подгруппу либо на недоступный предмет')
        return message
    elif status_code == "LOCKED":
        message = types.Message(text=f'Это место уже занято, введите другое')
        return message
    elif status_code == "NOT_ACCEPTABLE":
        message = types.Message(text=f'Нельзя записаться на предмет дальше, чем 2 недели')
        return message
    else:
        message = types.Message(text='Произошла непредвиденная ошибка, пожалуйста попробуйте позже')
        return message


def add_student(callback_data, telegram_id) -> str:
    print(callback_data)

    if register.is_registered(telegram_id):
        try:
            r = requests.post(url=BASE_API_URL + "putIntoTheQueue", json=callback_data)
            return r.text.replace('"', '')
        except requests.exceptions:
            return ""
