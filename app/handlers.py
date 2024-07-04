
import os
import csv
import random
import torch
import faiss
import requests
import numpy as np
from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified
from aiogram.types import CallbackQuery
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from sentence_transformers import SentenceTransformer, util
import pandas as pd
from asyncio import Lock


import app.keyboards as kb
# from app.model import process_filters
from app.model import search
from app.feedback import update_feedback_rating
from app.upcoming_games import get_upcoming_games
from app.random_game_steam import bot, send_random_game, save_game_data, update_game_rating, get_random_steam_game


######################################################################################################################

dp = Dispatcher(bot)

is_handle_text_running = False

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
    "Hey there! I'm GameExplorer, your ultimate gaming companion on Telegram! Ready to dive into the worlds of gaming? Let's roll!\n\n"
    "GameExplorer is a Telegram bot crafted to discover and recommend exciting games and DLCs straight from Steam. Whether you're into action-packed adventures or mind-bending puzzles, I've got you covered!\n\n"
    "<b>Key Features:</b>\n"
    "• <i>📝 Text-Based Recommendations:</i> Type in your preferences, and I'll use cutting-edge natural language processing to find games that match your style.\n"
    "• <i>🎲 Random Game:</i> Feeling spontaneous? I can surprise you with a random game or DLC suggestion from Steam.\n"
    "• <i>⭐ Game Ratings:</i> Love it or not so much? Rate the games I recommend to fine-tune future suggestions and keep track of your favorites.\n"
    "• <i>♥️ Add to Favorites:</i> Found a game you adore? Add it to your favorites list with just a tap!\n"
    "• <i>🕹️ Upcoming Games:</i> Wondering what's next? Ask about upcoming games, and I'll keep you updated on the latest releases!\n\n"
    "<b>Creators:</b>\n"
    "• <i>👩‍💻 @MossyHead:</i> Bringing the main functionalities to life.\n"
    "• <i>👨‍💻 @pulluptheroots:</i> Processing data and integrating machine learning magic.\n"
)

list_of_commands = (
        "<b>Main Commands:</b>\n"
        "• <i>/start:</i> Start interacting with the bot.\n"
        "• <i>/help:</i> Get a list of available commands.\n"
        "• <i>/info:</i> Information about the project.\n"
        "• <i>/filters:</i> Enter text queries to receive personalized game recommendations.\n"
        "• <i>/random:</i> Get a random game or DLC.\n"
        "• <i>/upcoming:</i> Get a list of upcoming games.\n"
        "• <i>/favorites:</i> Get a list of yours favorite games.\n\n"
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

# Обработчик команды /filters
@dp.message_handler(commands=['filters'])
async def show_filters(message: types.Message):
    user_id = message.from_user.id
    filters = user_filters.get(user_id, [])
    await message.reply("Select filters:", reply_markup=kb.get_filter_keyboard(filters))

@dp.callback_query_handler(lambda c: c.data.startswith('filter_'))
async def add_filter(callback_query: types.CallbackQuery):
    filter_name = callback_query.data.split('filter_')[1]
    user_id = callback_query.from_user.id
    if user_id not in user_filters:
        user_filters[user_id] = []
    if filter_name in user_filters[user_id]:
        user_filters[user_id].remove(filter_name)
        await bot.answer_callback_query(callback_query.id, text=f"Removed filter: {filter_name}")
    else:
        user_filters[user_id].append(filter_name)
        await bot.answer_callback_query(callback_query.id, text=f"Added filter: {filter_name}")
    filters = user_filters[user_id]
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=kb.get_filter_keyboard(filters))

@dp.callback_query_handler(lambda c: c.data == 'reset_filters')
async def reset_filters(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_filters[user_id] = []
    await bot.answer_callback_query(callback_query.id, text="Filters have been reset")
    filters = user_filters[user_id]
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=kb.get_filter_keyboard(filters))

@dp.callback_query_handler(lambda c: c.data == 'done_filters')
async def done_filters(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text="Filters selection done. Please enter your text.")
    await bot.send_message(callback_query.from_user.id, "Write your text in English.")

def make_default_filters():
    return [
        'single_player', 'family_library', 'MMO', 'action', 'indie', 'simulator',
        'strategy', 'casual', 'adventure', 'RPG', 'VR', 'share/split_screen', 
        'f2p', 'coop', 'multiplayer', 'racing/sport'
    ]
@dp.message_handler(lambda message: message.text and message.text.lower() not in ['/info', '/help', '/filters', '/random', '/upcoming', '/favorites', '/addfav'])
async def handle_user_text(message: types.Message):
    if message.from_user.id in user_filters:
        filters = user_filters[message.from_user.id]
        user_query = message.text
        recommendations = search(user_query, filters)
        if not recommendations:
            await message.reply("No recommendations found based on your filters.")
        else:
            for rec in recommendations:
                game_name = rec.get('name')
                game_appid = rec.get('steam_appid')
                game_url = f"https://store.steampowered.com/app/{game_appid}"
                keyboard = kb.create_rating_keyboard()
                favorite_button = types.InlineKeyboardButton(text="Add to favorites", callback_data="addfav_")
                keyboard.row(favorite_button)
                await message.reply(f'<b>{game_name}</b>\n\nGo to <a href="{game_url}"> Steam page.</a>\n\nAppID: {game_appid}', parse_mode='HTML', reply_markup=keyboard)
            await message.reply("Please rate these recommendations:", reply_markup=kb.feedback_keyboard())
    else:
        await message.reply("Please select filters first using /filters.")
    
######################################################################################################################




@dp.callback_query_handler(lambda query: query.data.startswith('feedback_'))
async def handle_feedback(callback_query: types.CallbackQuery):
    try:
        rating = int(callback_query.data.split('_')[1])
        telegram_user_id = callback_query.from_user.id
        user_input = callback_query.message.reply_to_message.text 

        recommendations = search(user_input, user_filters.get(telegram_user_id, []))

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        feedback_file = '/Users/mossyhead/ds_bootcamp/GameExplorer/app/users_db/feedback.csv'
        
        with open(feedback_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'date', 'telegram_user_id', 'user_input', 'game_name', 'steam_appid', 'rating'
            ])
            if file.tell() == 0:  # Check if file is empty
                writer.writeheader()
            
            for rec in recommendations:
                game_name = rec.get('name')
                game_appid = rec.get('steam_appid')
                writer.writerow({
                    'date': current_time,
                    'telegram_user_id': telegram_user_id,
                    'user_input': user_input,
                    'game_name': game_name,
                    'steam_appid': game_appid,
                    'rating': rating
                })
        
        await callback_query.message.edit_reply_markup(None)
        await callback_query.answer(f'You rated the recommendations with {rating} stars.')
    except ValueError as e:
        print(f"Error processing feedback rating: {e}")
        await callback_query.answer(f'Invalid rating. Please choose a number from 1 to 5.', show_alert=True)





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
    await save_game_data(telegram_user_id, game_name, game_id, rating)
    await update_game_rating(telegram_user_id, game_name, game_id, rating)
    await callback_query.message.edit_reply_markup(None)
    await callback_query.answer(f'You rated "{game_name}" with {rating} stars.')

# Обработчик команды /next
@dp.callback_query_handler(lambda query: query.data == 'next')
async def handle_next(callback_query: CallbackQuery):
    await send_random_game(callback_query.message)

######################################################################################################################
    
# Обработчик команды /upcoming
    
@dp.message_handler(commands=['upcoming'])
async def send_upcoming_games(message: types.Message):
    upcoming_games = get_upcoming_games()
    
    if upcoming_games:
        for game in upcoming_games[:3]: # Ограничимся первыми тремя играми для примера
            release_date = datetime.strptime(game['release_date'], "%d %b, %Y").date()
            today=datetime.today().date()
            if release_date == today:
                days_until_release = 'Just released'
            elif release_date > today:
                days_until_release = f'{(release_date - today).days} days left'
            else:
                days_until_release = f'{(today - release_date).days} days ago'
            
            formatted_message= (
                f"*{game['name']}*\n\n"
                f"Release Date: {game['release_date']} ({days_until_release})\n\n"
                f"Genre: {game['genre']}\n\n"
                f"OS: {game['os']}\n\n"
                f"[Link]({game['store_link']})\n\n"
            )
            await message.reply(formatted_message, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("Failed to fetch upcoming games.")


######################################################################################################################


@dp.callback_query_handler(lambda query: query.data.startswith('addfav_'))
async def handle_fav(callback_query: CallbackQuery):
    try:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        game_name = callback_query.message.text.split('\n\n')[0].replace('<b>', '').replace('</b>', '')
        game_id = callback_query.message.text.split('AppID: ')[-1].strip()
        telegram_user_id = callback_query.from_user.id
        game_url = f"https://store.steampowered.com/app/{game_id}"
        with open('/Users/mossyhead/ds_bootcamp/GameExplorer/app/users_db/favorites.csv', mode='a', newline='') as file:
            writer = csv.writer(file)

            if file.tell() == 0:  # Проверка, пустой ли файл
                writer.writerow(['Date', 'Telegram_User_ID', 'AppID', 'Name', 'Link'])  # Запись заголовков колонок
            writer.writerow([date, telegram_user_id, game_id, game_name, game_url])
        await callback_query.message.edit_reply_markup(None)
        await callback_query.answer(f"Game {game_name} added to favorites!")

    except Exception as e:
        await callback_query.answer(f"Failed to add game to favorites: {e}")
        print(f"Error adding game to favorites: {e}")

@dp.message_handler(commands=['favorites'])
async def send_favorites(message: types.Message):
    try:
        user_id = message.from_user.id
        favorites_list = []

        with open('/Users/mossyhead/ds_bootcamp/GameExplorer/app/users_db/favorites.csv', mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            favorites_list = [(row[3], row[4]) for row in reader if row[1] == str(user_id)]
        
        if favorites_list:
            favorites_info = "\n\n".join([f"{name} - <a href='{url}'>Game Link</a>" for name, url in favorites_list])
            await message.answer(f"Your favorite games:\n\n{favorites_info}", parse_mode=types.ParseMode.HTML)
        else:
            await message.answer("You haven't added any games to your favorites yet.")
    
    except FileNotFoundError:
        await message.answer("You haven't added any games to your favorites yet.")
    
    except Exception as e:
        await message.answer("Failed to fetch favorites. Please try again later.")
        print(f"Error fetching favorites: {e}")

