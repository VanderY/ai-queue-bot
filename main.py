import logging
import config
import TGCalendar.telegramcalendar as tgcalendar
from aiogram import Bot, Dispatcher, executor, types
import keyboards as kb
import Student
import register
import queue_api
from datetime import datetime

import api_queue_parser as api

ADMIN_ID = 465801855

# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=config.TG_API_TOKEN)
dp = Dispatcher(bot)


@dp.callback_query_handler(lambda c: c.data.startswith('lesson'))
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    parsed_data = queue_api.callback_to_json(str(callback_query.from_user.id) + ";" + callback_query.data)
    is_added = queue_api.add_student(parsed_data)
    print(is_added)
    date = datetime.strptime(parsed_data["date"], '%Y-%m-%d')
    if is_added:
        await bot.edit_message_text(text=f'Вы успешно записались на {parsed_data["qPlace"]} место\n'
                                         f'на {parsed_data["subject"]} {date.strftime("%d.%m.%Y")}',
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
    else:
        await bot.edit_message_text(text=f'Зарегистрируйтесь при помощи команды /reg Фамилия Имя',
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data.startswith('subgroup'))
async def callback_group(callback_query: types.CallbackQuery):
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


@dp.callback_query_handler(lambda c: c.data)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['calendar'])
async def calendar(message: types.Message):
    cld = tgcalendar.create_calendar()
    await message.answer('Пожалуйтса, выберите дату:', reply_markup=cld)


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
