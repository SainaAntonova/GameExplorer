import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers import dp  # Импорт диспетчера из handlers
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp.middleware.setup(LoggingMiddleware())
    dp['bot'] = bot  # Установка бота для диспетчера
    try:
        await dp.start_polling()
    except Exception as e:
        logging.exception(f"Error in polling: {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
    try:
        asyncio.run(main())
        print('Bot started.')
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped.')

