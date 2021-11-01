import json
import logging

import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

import api_queue_parser
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


@dp.message_handler(lambda m: m.text.startswith('❌Отменить действие❌'), state='*')
async def exit_state(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.answer("Действие отменено")
    await state.reset_state()


@dp.callback_query_handler(lambda c: c.data.startswith('lesson'))
async def process_lesson_callback(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    await state.set_state(StateMachine.all()[0])
    await bot.answer_callback_query(callback_query.id)
    await state.set_data(callback_query.data)
    data = str(await state.get_data())
    separated_data = data.split(";")
    closest_kb = InlineKeyboardMarkup(row_width=1)
    closest_kb.add(InlineKeyboardButton("Записаться на ближайшее свободное место", callback_data="closest"))
    lesson_data = api_queue_parser.get_subject_by_id(separated_data[1])
    # date = datetime.strptime(separated_data[4], '%Y-%m-%d')
    # students_list = queue_api.list_students(lesson_data)
    queue = api_queue_parser.get_queue_by_id(str(separated_data[1]))
    students = ""
    for student in queue:
        students += f"{student}\n"
    if students != "Queue is empty!\n":
        await bot.edit_message_text(f'Очередь на {lesson_data["lesson"]} {separated_data[2]} '
                                    f'{lesson_data["lessonTime"]}\n'
                                    f'{students}',
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    else:
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id)
    await callback_query.message.answer(text=f'\nНапишите предпочитаемый номер в очереди на '
                                             f'{separated_data[3]}({separated_data[4]}) {separated_data[2]}',
                                        reply_markup=closest_kb)


@dp.callback_query_handler(lambda c: c.data.startswith('closest'), state=StateMachine.QUEUE_NUMBER_WAITING)
async def closest_place_choose(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    id_data = str(await state.get_data()).split(";")
    lesson_data = api_queue_parser.get_subject_by_id(id_data[1])
    is_added = queue_api.queue_json_to_add(id_data[1], None, callback_query.message.chat.id, id_data[2], "true")
    # is_added = queue_api.add_student(lesson_data, str(message.from_user.id))
    print(is_added)

    if is_added == "ACCEPTED":
        await state.reset_state()
        queue = api_queue_parser.get_queue_by_id(str(id_data[1]))
        students = ""
        for student in queue:
            students += f"{student}\n"
        await callback_query.message.answer(f'Очередь на {lesson_data["lesson"]}'
                                            f' {lesson_data["lessonTime"]}\n'
                                            f'{students}')
        await callback_query.answer()
    elif is_added == "CONFLICT":
        keyboard = kb.yes_no_keyboard(callback_query.message.text)
        await callback_query.message.answer(text=f'Вы уже записаны в очередь на {lesson_data["lesson"]}'
                                                 f' {lesson_data["lessonTime"]}, '
                                                 f'хотите перезаписаться?',
                                            reply_markup=keyboard)
    elif is_added == "BAD_REQUEST":
        await callback_query.answer(text=f'Введите корректное значение')
    elif is_added == "BAD_GATEWAY":
        await callback_query.answer(text=f'Вы пытаетесь записаться не в свою подгруппу')
    elif is_added == "LOCKED":
        await callback_query.answer(text=f'Это место уже занято, введите другое')
    elif is_added == "NOT_ACCEPTABLE":
        await callback_query.answer(text=f'Нельзя записаться на предмет дальше, чем 2 недели')
    else:
        await state.reset_state()
        await callback_query.answer('Произошла непредвиденная ошибка, пожалуйста попробуйте позже')


@dp.message_handler(state=StateMachine.QUEUE_NUMBER_WAITING)
async def place_in_queue_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    # parsed_data = queue_api.callback_to_json(str(message.from_user.id)
    #                                          + ";" + str(await state.get_data())
    #                                          + ";" + message.text)
    id_data = str(await state.get_data()).split(";")
    lesson_data = api_queue_parser.get_subject_by_id(id_data[1])
    is_added = queue_api.queue_json_to_add(id_data[1], message.text, message.from_user.id, id_data[2])
    # is_added = queue_api.add_student(lesson_data, str(message.from_user.id))
    print(is_added)

    if is_added == "ACCEPTED":
        await state.reset_state()
        queue = api_queue_parser.get_queue_by_id(str(id_data[1]))
        students = ""
        for student in queue:
            students += f"{student}\n"
        await message.answer(f'Очередь на {lesson_data["lesson"]}'
                             f' {lesson_data["lessonTime"]}\n'
                             f'{students}')
    elif is_added == "CONFLICT":
        keyboard = kb.yes_no_keyboard(message.text)
        await message.answer(text=f'Вы уже записаны в очередь на {lesson_data["lesson"]} {lesson_data["lessonTime"]}, '
                                  f'хотите перезаписаться?',
                             reply_markup=keyboard)
    elif is_added == "BAD_REQUEST":
        await message.answer(text=f'Введите корректное значение')
    elif is_added == "BAD_GATEWAY":
        await message.answer(text=f'Вы пытаетесь записаться не в свою подгруппу')
    elif is_added == "LOCKED":
        await message.answer(text=f'Это место уже занято, введите другое')
    elif is_added == "NOT_ACCEPTABLE":
        await message.answer(text=f'Нельзя записаться на предмет дальше, чем 2 недели')
    else:
        await state.reset_state()
        await message.answer('Произошла непредвиденная ошибка, пожалуйста попробуйте позже')


@dp.callback_query_handler(lambda c: c.data.startswith('choose'), state=StateMachine.QUEUE_NUMBER_WAITING)
async def rewriting_yes_no_choose(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    data = str(await state.get_data())
    separated_state_data = data.split(";")
    separated_callback_data = callback_query.data.split(";")
    date = datetime.strptime(separated_state_data[2], '%Y-%m-%d')
    await bot.answer_callback_query(callback_query.id)
    if separated_callback_data[1] == "yes":
        id_data = str(await state.get_data()).split(";")
        lesson_data = api_queue_parser.get_subject_by_id(id_data[1])
        is_added = queue_api.queue_json_to_add(id_data[1], separated_callback_data[2],
                                               callback_query.message.chat.id, id_data[2], "true")
        print(is_added)

        if is_added == "ACCEPTED":
            queue = api_queue_parser.get_queue_by_id(str(id_data[1]))
            students = ""
            for student in queue:
                students += f"{student}\n"
            await callback_query.message.answer(f'Очередь на {lesson_data["lesson"]}'
                                                f' {lesson_data["lessonTime"]}\n'
                                                f'{students}')
            await state.reset_state()
        elif is_added == "CONFLICT":
            keyboard = kb.yes_no_keyboard(separated_callback_data[2])
            await callback_query.message.answer(
                text=f'Вы уже записаны в очередь на {lesson_data["lesson"]} {lesson_data["lessonTime"]}, '
                     f'хотите перезаписаться?',
                reply_markup=keyboard)
        elif is_added == "BAD_REQUEST":
            await callback_query.message.answer(text=f'Введите корректное значение')
        elif is_added == "BAD_GATEWAY":
            await callback_query.answer(text=f'Вы пытаетесь записаться не в свою подгруппу')
        elif is_added == "LOCKED":
            await callback_query.message.answer(text=f'Это место уже занято, введите другое')
        elif is_added == "NOT_ACCEPTABLE":
            await callback_query.answer(text=f'Нельзя записаться на предмет дальше, чем 2 недели')
        else:
            await state.reset_state()
            await callback_query.message.answer('Произошла непредвиденная ошибка, пожалуйста попробуйте позже')
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
    id_data = str(await state.get_data()).split(";")
    is_added = queue_api.queue_json_to_add(id_data[1], message.text, message.from_user.id, id_data[2], "true")
    print(is_added)
    lesson_data = api_queue_parser.get_subject_by_id(id_data[1])
    if is_added == "ACCEPTED":
        await state.reset_state()
        await message.answer(f'Вы успешно записались на {message.text} место\n'
                             f'на {lesson_data["lesson"]} {lesson_data["lessonTime"]}')
    elif is_added == "CONFLICT":
        keyboard = kb.yes_no_keyboard(message.text)
        await message.answer(text=f'Вы уже записаны в очередь на {lesson_data["lesson"]} {lesson_data["lessonTime"]}, '
                                  f'хотите перезаписаться?',
                             reply_markup=keyboard)
    elif is_added == "BAD_REQUEST":
        await message.answer(text=f'Введите корректное значение')
    elif is_added == "BAD_GATEWAY":
        await message.answer(text=f'Вы пытаетесь записаться не в свою подгруппу')
    elif is_added == "LOCKED":
        await message.answer(text=f'Это место уже занято, введите другое')
    elif is_added == "NOT_ACCEPTABLE":
        await message.answer(text=f'Нельзя записаться на предмет дальше, чем 2 недели')
    else:
        await state.reset_state()
        await message.answer('Произошла непредвиденная ошибка, пожалуйста попробуйте позже')


@dp.callback_query_handler(lambda c: c.data.startswith('subgroup'))
async def callback_subgroup(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    name = await state.get_data()
    telegram_id = callback_query.message.chat.id
    register_status = register.register(callback_query.data, name, telegram_id)
    await bot.answer_callback_query(callback_query.id)
    if register_status == "ACCEPTED":
        await bot.edit_message_text(text="Вы успешно зарегистрировались!",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    elif register_status == "CONFLICT":
        await bot.edit_message_text(text="Пользователь с таким telegramId уже существует\n"
                                         "(Пасхалка!!!!!! напиши /anekdot там смешно(честно))",
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


@dp.message_handler(lambda m: m.text.startswith('📝Записаться в очередь📝'))
@dp.message_handler(commands=['queue'])
async def calendar(message: types.Message):
    if register.is_registered(message.from_user.id):
        cld = tgcalendar.create_calendar()
        await message.answer('Пожалуйста, выберите дату:', reply_markup=cld)
    else:
        await message.answer('Зарегистрируйтесь при помощи команды /reg')


@dp.callback_query_handler(lambda c: c.data.startswith('IGNORE'))
@dp.callback_query_handler(lambda c: c.data.startswith('PREV-MONTH'))
@dp.callback_query_handler(lambda c: c.data.startswith('DAY'))
@dp.callback_query_handler(lambda c: c.data.startswith('NEXT-MONTH'))
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data)
async def answer_default_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()


@dp.message_handler(state=StateMachine.REGISTRATION_STATE)
async def register_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    name = message.text
    print("register name: " + message.text)
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
    exit_state_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    exit_state_kb.add(types.KeyboardButton(text="📝Записаться в очередь📝"))
    exit_state_kb.add(types.KeyboardButton(text="❌Отменить действие❌"))
    if register.is_registered(telegram_id):
        await message.answer(f"Вы уже зарегистрированы", reply_markup=exit_state_kb)
    else:
        state = dp.current_state(user=message.chat.id)
        await state.set_state(StateMachine.all()[1])
        await message.answer("Введите свою Фамилию и Имя", reply_markup=exit_state_kb)


if __name__ == '__main__':
    executor.start_polling(dp)
