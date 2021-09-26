import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_lessons(lessons, date):
    lessons_keyboard = InlineKeyboardMarkup(row_width=1)
    i = 1
    for lesson in lessons:
        lesson_btn = InlineKeyboardButton(
            str(i) + ". " + lesson['lesson'] + " (" + lesson['lessonType'] + ") " + (
                str(lesson['subgroup']) + " подгр." if lesson['subgroup'] != 0 else ""),
            callback_data="lesson;" + lesson['lesson'] + ";" + lesson['lessonType'] + ";" + str(lesson['subgroup']) + ";" + date)
        lessons_keyboard.add(lesson_btn)
        i += 1
    return lessons_keyboard


def group_choose(groups):
    group_keyboard = InlineKeyboardMarkup(row_width=1)
    for group in groups:
        group_btn = InlineKeyboardButton(group, group)
        group_keyboard.add(group_btn)
    return group_keyboard
