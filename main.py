import json
import logging

import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from StateMachine import StateMachine
import config
import TGCalendar.telegramcalendar as tgcalendar
from aiogram import Bot, Dispatcher, executor, types
import keyboards as kb
import Student
import register
import queue_api
from datetime import datetime
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import api_queue_parser as api

ADMIN_ID = 465801855

# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=config.TG_API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.callback_query_handler(lambda c: c.data.startswith('lesson'))
async def process_lesson_callback(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    await state.set_state(StateMachine.all()[0])
    await bot.answer_callback_query(callback_query.id)
    await state.set_data(callback_query.data)
    data = str(await state.get_data())
    separated_data = data.split(";")

    date = datetime.strptime(separated_data[4], '%Y-%m-%d')
    await bot.edit_message_text(text=f'Напишите предпочитаемый номер в очереди на '
                                     f'{separated_data[1]}({separated_data[2]}) {date.strftime("%d.%m.%Y")}',
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id)


@dp.message_handler(state=StateMachine.QUEUE_NUMBER_WAITING)
async def place_in_queue_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    parsed_data = queue_api.callback_to_json(str(message.from_user.id)
                                             + ";" + str(await state.get_data())
                                             + ";" + message.text)
    is_added = queue_api.add_student(parsed_data)
    print(is_added)
    date = datetime.strptime(parsed_data["date"], '%Y-%m-%d')
    if is_added == "ACCEPTED":
        await state.reset_state()
        await message.answer(f'Вы успешно записались на {parsed_data["qplace"]} место\n'
                             f'на {parsed_data["subject"]} {date.strftime("%d.%m.%Y")}')
    elif is_added == "CONFLICT":
        keyboard = kb.yes_no_keyboard(message.text)
        await message.answer(text=f'Вы уже записаны в очередь на {parsed_data["subject"]} {date.strftime("%d.%m.%Y")}, '
                                  f'хотите перезаписаться?',
                             reply_markup=keyboard)
    elif is_added == "BAD_REQUEST":
        await message.answer(text=f'Введите корректное значение')
    elif is_added == "LOCKED":
        await message.answer(text=f'Это место уже занято, введите другое')
    else:
        await message.answer('Произошла непредвиденная ошибка, пожалуйста попробуйте позже')


@dp.callback_query_handler(lambda c: c.data.startswith('choose'), state=StateMachine.QUEUE_NUMBER_WAITING)
async def rewriting_yes_no_choose(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    data = str(await state.get_data())
    separated_state_data = data.split(";")
    separated_callback_data = callback_query.data.split(";")
    date = datetime.strptime(separated_state_data[4], '%Y-%m-%d')
    await bot.answer_callback_query(callback_query.id)
    if separated_callback_data[1] == "yes":
        await bot.edit_message_text(text=f'Введите новое место в очереди на '
                                         f'{separated_state_data[1]}({separated_state_data[2]}) {date.strftime("%d.%m.%Y")}',
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        await state.set_state(StateMachine.all()[2])
    elif separated_callback_data[1] == "no":
        await state.reset_state()
        await bot.edit_message_text(text="Хорошо.\nЕсли захотите записаться на другой предмет, пишите /queue",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    else:
        await bot.edit_message_text(text="Произошла непредвиденная ошибка",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)


@dp.message_handler(state=StateMachine.REWRITING_QUEUE_NUMBER)
async def place_in_queue_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    await state.reset_state()
    await message.answer('Заглушка для изменения места в очереди')


@dp.callback_query_handler(lambda c: c.data.startswith('subgroup'))
async def callback_subgroup(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    name = await state.get_data()
    telegram_id = callback_query.message.chat.id
    register_status = register.register(callback_query.data, name, telegram_id)
    await bot.answer_callback_query(callback_query.id)
    if register_status == "ACCEPTED":
        await bot.edit_message_text(text="Вы успешно зарегестрировались!",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    elif register_status == "CONFLICT":
        await bot.edit_message_text(text="Пользователь с таким telegramId уже существует",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    else:
        await bot.edit_message_text(text="Произошла непредвиденная ошибка :(",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data.startswith('group'))
async def callback_group(callback_query: types.CallbackQuery):
    subgroups = kb.get_subgroup(callback_query.data)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text=f'Выберите свою подгруппу:',
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=subgroups)


@dp.message_handler(commands=['anekdot'])
async def random_anekdot(message: types.Message):
    try:
        url = "http://rzhunemogu.ru/RandJSON.aspx?CType=11"
        r = requests.get(url=url)
        raw = r.text.replace("\n", " ").replace("\r", " ")
        print(raw)
        anekdot = json.loads(raw)
        await message.answer(anekdot["content"])
    except json.decoder.JSONDecodeError:
        await message.answer("Что-то пошло не так :(\nПопробуйте еще раз")


@dp.message_handler(commands=['queue'])
async def calendar(message: types.Message):
    if register.is_registered(message.from_user.id):
        cld = tgcalendar.create_calendar()
        await message.answer('Пожалуйтса, выберите дату:', reply_markup=cld)
    else:
        await message.answer('Зарегистрируйтесь при помощи команды /reg Фамилия Имя')


@dp.callback_query_handler(lambda c: c.data)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(state=StateMachine.REGISTRATION_STATE)
async def register_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    name = message.text

    if name == "":
        await message.answer(f"Вам нужно корректно написать свою фамилию и имя!\nФормат: Фамилия Имя")
    else:
        groups_kb = kb.group_choose(["921701", "921702", "921703", "921704"])
        await message.answer(f"Выберите свою группу:", reply_markup=groups_kb)

    await state.reset_state()
    await state.set_data(name)


@dp.message_handler(commands=['reg', 'start'])
async def reg(message: types.Message):
    telegram_id = message.from_user.id
    if register.is_registered(telegram_id):
        await message.answer(f"Вы уже зарегистрированы")
    else:
        state = dp.current_state(user=message.chat.id)
        await state.set_state(StateMachine.all()[1])
        await message.answer("Введите свою Фамилию и Имя")


if __name__ == '__main__':
    executor.start_polling(dp)
