import sqlite3 as sq
from datetime import datetime


def create_db():
    conn = sq.connect('game_ratings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP,
            telegram_user_id INTEGER,
            appid INTEGER,
            name TEXT,
            user_rating INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_rating_to_db(date, telegram_user_id, appid, name, user_rating):
    conn = sq.connect('game_ratings.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ratings (date, telegram_user_id, appid, name, user_rating)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, telegram_user_id, appid, name, user_rating))
    conn.commit()
    conn.close()

def main():
    create_db()
    date = datetime.now()
    telegram_user_id = 123456789  # Замените на реальный ID пользователя Telegram
    appid = 12345  # ID приложения Steam
    name = "Example Game"
    user_rating = 4  # Оценка пользователя от 1 до 5

    # Добавляем оценку в базу данных
    add_rating_to_db(date, telegram_user_id, appid, name, user_rating)

if __name__ == "__main__":
    main()
