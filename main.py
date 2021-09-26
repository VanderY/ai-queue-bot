import logging
import config
import TGCalendar.telegramcalendar as tgcalendar
from aiogram import Bot, Dispatcher, executor, types

import api_queue_parser as api

ADMIN_ID = 465801855

# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=config.TG_API_TOKEN)
dp = Dispatcher(bot)


# ------------------------Queue placement-----------------------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith('lesson'))
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    # data.collect_data(callback_query.data, callback_query.from_user.id)
    username = callback_query.from_user.username
    await bot.edit_message_text(text=f'Заглушка для записи в очередь\n@{username} выбрал {callback_query.data}',
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id)
    # await bot.send_message(callback_query.from_user.id, 'Пожалуйста, напишите свой номер телефона')
# ------------------------Queue placement-----------------------------------------------------


@dp.callback_query_handler(lambda c: c.data)
async def callback_calendar(callback_query: types.CallbackQuery):
    response = tgcalendar.process_calendar_selection(bot, callback_query)
    # data.collect_data(response[2], callback_query.from_user.id)
    await response[0]
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['calendar'])
async def calendar(message: types.Message):
    cld = tgcalendar.create_calendar()
    await message.answer('Пожалуйтса, выберите дату:', reply_markup=cld)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer("Здарова!\n"
                         "Я тестовый бот\n"
                         "Напиши /calendar чтобы протестировать самую свежую функцию!")


if __name__ == '__main__':
    executor.start_polling(dp)
