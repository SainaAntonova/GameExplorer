import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from app.handlers import dp  # Импорт диспетчера из handlers
from aiogram.contrib.middlewares.logging import LoggingMiddleware


# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('No BOT_TOKEN provided')

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp.middleware.setup(LoggingMiddleware())
    dp['bot'] = bot  # Установка бота для диспетчера
    try:
        await dp.start_polling()
    except Exception as e:
        logging.exception(f"Error in polling: {e}")

if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    logging.basicConfig(level=logging.INFO)  # Настройка логирования
    try:
        asyncio.run(main())
        print('Bot started.')
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped.')

