#!/usr/bin/env python3
#
# A library that allows to create an inline calendar keyboard.
# grcanosa https://github.com/grcanosa
#
"""
Base methods for calendar keyboard creation and processing.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from dateutil.parser import parse
import api_queue_parser as api
import keyboards as kb
import datetime
import calendar


def create_callback_data(action, year, month, day):
    """ Create the callback data associated to each button"""
    return ";".join([action, str(year), str(month), str(day)])


def separate_callback_data(data):
    """ Separate the callback data"""
    return data.split(";")


def create_calendar(year=None, month=None):
    """
    Create an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    """
    now = datetime.datetime.now()
    if year is None: year = now.year
    if month is None: month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = InlineKeyboardMarkup(row_width=7)
    # First row - Month and Year
    row = []
    keyboard.add(InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore))
    # Second row - Week Days
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(InlineKeyboardButton(day, callback_data=data_ignore))
    slot1 = row[0]
    slot2 = row[1]
    slot3 = row[2]
    slot4 = row[3]
    slot5 = row[4]
    slot6 = row[5]
    slot7 = row[6]
    keyboard.row(slot1, slot2, slot3, slot4, slot5, slot6, slot7)

    week_number = 0
    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        week_number += 1
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day),
                                                callback_data=create_callback_data("DAY", year, month, day)))
        slot1 = row[0]
        slot2 = row[1]
        slot3 = row[2]
        slot4 = row[3]
        slot5 = row[4]
        slot6 = row[5]
        slot7 = row[6]
        keyboard.row(slot1, slot2, slot3, slot4, slot5, slot6, slot7)
    # Last row - Buttons
    row = []
    slot1 = InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day))
    slot2 = InlineKeyboardButton(" ", callback_data=data_ignore)
    slot3 = InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day))
    keyboard.row(slot1, slot2, slot3)
    # keyboard.add(row)

    return keyboard


def process_calendar_selection(bot, query):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    """
    choose = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton('Да', callback_data='yes')
    no = InlineKeyboardButton('Нет', callback_data='no')
    choose.row(yes, no)

    ret_data = (bot.answer_callback_query(callback_query_id=query.id),
                False, None)
    (action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        response = bot.answer_callback_query(callback_query_id=query.id)
        ret_data = response, False, None
    elif action == "DAY":
        date = str(year) + "-" + str(month) + "-" + str(day)
        lessons = api.get_schedule(921703, date)
        response = bot.edit_message_text(text=f'Дата: {day}-{month}-{year}\nВыберите предмет:',
                                         chat_id=query.message.chat.id,
                                         message_id=query.message.message_id,
                                         reply_markup=kb.get_lessons(lessons, date)
                                         )
        ret_data = response, True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        response = bot.edit_message_text(text=query.message.text,
                                         chat_id=query.message.chat.id,
                                         message_id=query.message.message_id,
                                         reply_markup=create_calendar(int(pre.year), int(pre.month)))
        ret_data = response, False, None
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        response = bot.edit_message_text(text=query.message.text,
                                         chat_id=query.message.chat.id,
                                         message_id=query.message.message_id,
                                         reply_markup=create_calendar(int(ne.year), int(ne.month)))
        ret_data = response, False, None
    else:
        response = bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")
        ret_data = response, False, None
        # UNKNOWN
    return ret_data
