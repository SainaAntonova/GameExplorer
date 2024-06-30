import csv
import random
import torch
import faiss
import numpy as np
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from sentence_transformers import SentenceTransformer, util
import pandas as pd

import app.keyboards as kb
from app.random_game_steam import bot, send_random_game, save_game_data
from app.model import process_filters

######################################################################################################################

dp = Dispatcher(bot)

stickers = [
    'CAACAgIAAxkBAAEGZE1meWKo7rubTuI-aD07TdISrpnsNQACf04AAoDrgUkxIxOxMDuljzUE',
    'CAACAgIAAxkBAAEGea9mfW0ow0_vfWTpP_cFNTnX1I2v2AAC-z0AAiNDwUvvqtPBSqpFGzUE',
    'CAACAgQAAxkBAAEGealmfWyv04e6appVyMMqQSw509noBwACdQAD-OAEAuzUgS8hwRBVNQQ',
    'CAACAgIAAxkBAAEGeaNmfWxtzHgHLJHxaqPM_oWRp_MyYAAC1BQAAnorGEmQ5IrFt8_dcjUE',
    'CAACAgIAAxkBAAEGeaFmfWuA2iRMviLz4oy3GsuXCTgvLQACmggAAlwCZQPJwLXM0kXbjDUE',
    'CAACAgIAAxkBAAEGeZlmfWtCLxaDFf_6MJ3v33BY6grGGgACGwEAAltFdxCLo9RGF2iNoTUE',
    'CAACAgIAAxkBAAEGeZdmfWr3We4nHaXOrLIg7GaSI9TEjAACRF4AAi3haEi5O6MC2jMvlTUE',
    'CAACAgIAAxkBAAEGeZVmfWrGFNU0Z8SW-jpD96tgUkZ9fgACLQADFUHSEoXqddO54HSvNQQ',
    'CAACAgIAAxkBAAEGebdmfW3kEGqcOrKs71sAAaFCdPMuu2AAAg4bAAKcIrhJGknEH9eL5Cs1BA',
]

project_info = (
        "🎮<b>About the Project:</b>🎮\n\n"
        "GameExplorer is a Telegram bot designed to search and recommend games and DLCs from Steam. "
        "The project is developed to help users discover new games based on their preferences, provide random game recommendations, and allow users to rate games.\n\n"
        "<b>Key Features:</b>\n"
        "• <i>Text-Based Recommendations:</i> Users can input text queries, and the bot will search for and recommend games based on the input text using natural language processing models.\n"
        "• <i>Random Game:</i> The bot can suggest a random game or DLC from Steam.\n"
        "• <i>Game Rating:</i> Users can rate the recommended games, which helps improve recommendations and track their preferences.\n\n"
       "<b>Authors:</b>\n"
        "• <i>@MossyHead:</i> Development of the main functionality of the bot.\n"
        "• <i>@pulluptheroots:</i> Data processing and integration of machine learning models.\n"
    )

list_of_commands = (
        "<b>Main Commands:</b>\n"
        "• <i>/start:</i> Start interacting with the bot.\n"
        "• <i>/help:</i> Get a list of available commands.\n"
        "• <i>/info:</i> Information about the project.\n"
        "• <i>/filters:</i> Enter text queries to receive personalized game recommendations.\n"
        "• <i>/random:</i> Get a random game or DLC.\n\n"
)
######################################################################################################################

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    sticker_id = random.choice(stickers)
    await message.answer_sticker(sticker=sticker_id)
    await message.reply(f'Hello, {message.from_user.full_name}!', reply_markup=kb.main)

######################################################################################################################

# Обработчик команды /help
@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.answer(list_of_commands, parse_mode=ParseMode.HTML)

######################################################################################################################

# Обработчик команды /info
@dp.message_handler(commands=['info'])
async def cmd_info(message: types.Message):
    await message.answer(project_info, parse_mode=ParseMode.HTML)

######################################################################################################################
user_filters = {}

# Команда /filters
@dp.message_handler(commands=['filters'])
async def cmd_filters(message: types.Message):
    await message.reply("Choose filters by OS:", reply_markup=kb.filter_keyboard("os"))

# Обработчик кнопок выбора операционной системы
@dp.callback_query_handler(lambda query: query.data.startswith('os_'))
async def process_os(callback_query: types.CallbackQuery):
    os_choice = callback_query.data.split('_')[1]
    await bot.send_message(callback_query.from_user.id, "Choose filters by genre:", reply_markup=kb.filter_keyboard("genre"))
    await callback_query.answer()
    # os_choice = callback_query.data.split('_')[1]
    # user_id = callback_query.from_user.id
    # if user_id not in user_filters:
    #     user_filters[user_id] = {}
    # user_filters[user_id]['os'] = None if os_choice == 'none' else os_choice
    # await bot.send_message(callback_query.from_user.id, "Choose filters by genre:", reply_markup=kb.filter_keyboard("genre"))
    # await callback_query.answer()

# Обработчик кнопок выбора жанра
@dp.callback_query_handler(lambda query: query.data.startswith('genre_'))
async def process_genre(callback_query: types.CallbackQuery):
    genre_choice = callback_query.data.split('_')[1]
    await bot.send_message(callback_query.from_user.id, "Write your text:")
    await callback_query.answer()
    # genre_choice = callback_query.data.split('_')[1]
    # user_id = callback_query.from_user.id
    # if user_id not in user_filters:
    #     user_filters[user_id] = {}
    # user_filters[user_id]['genre'] = None if genre_choice == 'none' else genre_choice
    # await bot.send_message(callback_query.from_user.id, "Write your text:")
    # await callback_query.answer()

# Обработка текстового сообщения после выбора фильтров
@dp.message_handler(lambda message: message.text and message.text.lower() not in ['/filters', '/random'])
async def handle_text(message: types.Message):
    recommendations = process_filters(message.text)
    for rec in recommendations:
        await message.reply(rec, parse_mode=ParseMode.HTML)

    # user_id = message.from_user.id
    # os_filter = user_filters.get(user_id, {}).get('os')
    # genre_filter = user_filters.get(user_id, {}).get('genre')
    # recommendations = process_filters(message.text, os_filter, genre_filter)
    # for rec in recommendations:
    #     await message.reply(rec, parse_mode=ParseMode.HTML)









######################################################################################################################
# Обработчик команды /random
@dp.message_handler(commands=['random'])
async def cmd_random(message: types.Message):
        await send_random_game(message)

# Обработчик команды /rate
@dp.callback_query_handler(lambda query: query.data == 'rate')
async def handle_rate(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(kb.create_rating_keyboard())

# Обработчик команды /rate и сохранения оценки в базе данных
@dp.callback_query_handler(lambda query: query.data.startswith('rate_'))
async def handle_rating(callback_query: CallbackQuery):
    rating = int(callback_query.data.split('_')[1])
    game_name = callback_query.message.text.split('\n\n')[0].replace('<b>', '').replace('</b>', '')

    
    # Сохранение оценки в базе данных или файл (здесь можно вставить ваш код)
    game_id = callback_query.message.text.split('AppID: ')[-1].strip()
    telegram_user_id = callback_query.from_user.username
    await update_game_rating(telegram_user_id, game_name, game_id, rating)
    await save_game_data(telegram_user_id, game_name, game_id, rating)
    await callback_query.message.edit_reply_markup(None)
    await callback_query.answer(f'You rated "{game_name}" with {rating} stars.')

async def update_game_rating(telegram_user_id, game_name, game_id, rating):
    # Чтение данных из CSV файла
    with open('/Users/mossyhead/ds_bootcamp/GameExplorer/app/users_db/user_ratings.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Поиск строки с данными для обновления
    for row in rows:
        if row[1] == game_id:
            row[3]= game_name
            row[2] = int(telegram_user_id) # Обновление ID пользователя
            row[4] = rating # Обновление оценки

    # Запись обновленных данных в CSV файл
    with open('/Users/mossyhead/ds_bootcamp/GameExplorer/app/users_db/user_ratings.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# Обработчик команды /next
@dp.callback_query_handler(lambda query: query.data == 'next')
async def handle_next(callback_query: CallbackQuery):
    await send_random_game(callback_query.message)


######################################################################################################################

# Обработчик всех остальных текстовых сообщений
@dp.message_handler()
async def handle_text(message: types.Message):
    await message.answer('I don\'t understand you! Please, write /help.')
