import logging

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


@dp.callback_query_handler(lambda c: c.data.startswith('lesson'), state=StateMachine.QUEUE_NUMBER_WAITING)
async def process_lesson_callback(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.message.chat.id)
    await state.set_state(StateMachine.all()[0])
    await bot.answer_callback_query(callback_query.id)
    await state.set_data(callback_query.data)
    await bot.edit_message_text(text=f'Напишите предпочитаемый номер в очереди\n{str(await state.get_data())}',
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id)


@dp.message_handler(state=StateMachine.QUEUE_NUMBER_RECEIVED)
async def place_in_queue_message(message: types.Message):
    state = dp.current_state(user=message.chat.id)
    parsed_data = queue_api.callback_to_json(str(message.from_user.id)
                                             + ";" + str(await state.get_data())
                                             + ";" + message.text)
    is_added = queue_api.add_student(parsed_data)
    print(is_added)
    date = datetime.strptime(parsed_data["date"], '%Y-%m-%d')
    if is_added:
        await message.answer(f'Вы успешно записались на {parsed_data["qplace"]} место\n'
                             f'на {parsed_data["subject"]} {date.strftime("%d.%m.%Y")}')
    else:
        await message.answer('Произошла непредвиденная ошибка, пожалуйста попробуйте позже')


@dp.callback_query_handler(lambda c: c.data.startswith('subgroup'))
async def callback_subgroup(callback_query: types.CallbackQuery):
    parsed_data = register.callback_to_json(callback_query.data)
    register_status = register.register(parsed_data)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text="Вы успешно зарегестрировались!",
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


@dp.message_handler(commands=['calendar'])
async def calendar(message: types.Message):
    if register.is_registered(message.from_user.id):
        state = dp.current_state(user=message.chat.id)
        await state.reset_state()
        await state.set_state(StateMachine.all()[1])
        cld = tgcalendar.create_calendar()
        await message.answer('Пожалуйтса, выберите дату:', reply_markup=cld)
    else:
        await message.answer('Зарегистрируйтесь при помощи команды /reg Фамилия Имя')


@dp.callback_query_handler(lambda c: c.data, state=StateMachine.QUEUE_NUMBER_WAITING)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['reg'])
async def reg(message: types.Message):
    args = message.get_args()
    telegram_id = message.from_user.id
    if register.is_registered(telegram_id):
        await message.answer(f"Вы уже зарегестрированы")
    else:
        student = Student
        student.telegram_id = str(telegram_id)
        student.name = str(args)
        groups_kb = kb.group_choose(["921701", "921702", "921703", "921704"], student)
        await message.answer(f"Выберите свою группу:", reply_markup=groups_kb)


@dp.message_handler(commands=['group'])
async def group(message: types.Message):
    args = message.get_args()
    await message.answer(f"Args: {args}")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    username = message.from_user.username
    telegram_id = message.from_user.id
    await message.answer(f"Привет {username}!\n"
                         f"Твой telegram_id: {telegram_id}")


if __name__ == '__main__':
    executor.start_polling(dp)
