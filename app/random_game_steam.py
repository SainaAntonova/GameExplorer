import os
import csv
import html
import random
import requests
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.types import ParseMode


from app.keyboards import create_rating_keyboard, create_initial_keyboard

load_dotenv()
TG_API_TOKEN = os.getenv('BOT_TOKEN')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

bot = Bot(token=TG_API_TOKEN)


def get_random_steam_game():
    url = f'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
    response = requests.get(url)
    app_list = response.json()['applist']['apps']

    # Фильтрация только по играм и DLC
    while True:
        random_game = random.choice(app_list)
        game_id = random_game['appid']
        game_details = get_app_details(game_id)
        
        if game_details and game_details['type'] in ['game', 'dlc']:
            return game_details
def get_app_details(appid):
    url = f'http://store.steampowered.com/api/appdetails?appids={appid}'
    response = requests.get(url)
    data = response.json()

    if data[str(appid)]['success']:
        return data[str(appid)]['data']
    return None


async def send_random_game(message: types.Message, keyboard=None):
    random_game = get_random_steam_game()
    game_name = random_game['name']
    game_id = random_game['steam_appid']
    game_url = f'http://store.steampowered.com/app/{game_id}'
    plarform = ", ".join([key.capitalize() for key, value in random_game['platforms'].items() if value])
    game_type = random_game['type']
    genres = ", ".join([genre['description'] for genre in random_game.get('genres', [])])
    # Формирование информации о игре
    game_info = (
        f'<b>{game_name}</b>\n\n'
        f'Go to<a href="{game_url}">link.</a>\n\n'
        f'OS: {plarform}\n\n'
        f'Type: {game_type}\n\n'
        f'Genre: {genres}\n\n'
        f'AppID: {game_id}'
        
        
    )
    if keyboard is None:
        keyboard = create_initial_keyboard()

    await message.answer(game_info, parse_mode=ParseMode.HTML, reply_markup=keyboard )
    

async def save_game_data(telegram_user_id, game_name, game_id, rating):
    # Определение текущей даты и времени
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Добавление данных в CSV файл
    with open('/Users/mossyhead/ds_bootcamp/GameExplorer/app/users_db/user_ratings.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Проверка, пустой ли файл
            writer.writerow(['Date', 'Telegram_User_ID', 'AppID', 'Name', 'User_Rating'])  # Запись заголовков колонок
        
        
        if rating is not None:
            writer.writerow([current_time, telegram_user_id, game_id, game_name, rating])
        else:
            writer.writerow([current_time, telegram_user_id, game_id, game_name, ''])
        
  