import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import Student


def get_lessons(lessons, date):
    lessons_keyboard = InlineKeyboardMarkup(row_width=1)
    i = 1
    for lesson in lessons:
        lesson_btn = InlineKeyboardButton(
            str(i) + ". " + lesson['lesson'] + " (" + lesson['lessonType'] + ") " +
            (str(lesson['subgroup']) + " подгр." if lesson['subgroup'] != 0 else ""),
            callback_data="lesson;" + str(lesson['id']) + ";" + str(date) + ";" + str(lesson["lesson"]) + ";"
                          + str(lesson["lessonType"]))
        lessons_keyboard.add(lesson_btn)
        i += 1
    return lessons_keyboard


def group_choose(groups):
    group_keyboard = InlineKeyboardMarkup(row_width=1)
    for group in groups:
        group_btn = InlineKeyboardButton(group, callback_data="group;" + str(group))
        group_keyboard.add(group_btn)
    return group_keyboard


def get_subgroup(student_data):
    subgroup_keyboard = InlineKeyboardMarkup(row_width=2)
    subgroup1_btn = InlineKeyboardButton("1", callback_data="subgroup;1;" + student_data)
    subgroup2_btn = InlineKeyboardButton("2", callback_data="subgroup;2;" + student_data)
    return subgroup_keyboard.add(subgroup1_btn, subgroup2_btn)


def yes_no_keyboard(number_in_queue):
    yes_no_kb = InlineKeyboardMarkup(row_width=2)
    yes_btn = InlineKeyboardButton("Да", callback_data=f"choose;yes;{number_in_queue}")
    no_btn = InlineKeyboardButton("Нет", callback_data=f"choose;no;{number_in_queue}")
    return yes_no_kb.add(yes_btn, no_btn)
