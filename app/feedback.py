import csv
import os
import numpy as np
import pandas as pd




async def update_feedback_rating(telegram_user_id, user_input, recommendation, rating):
    feedback_file = '/Users/mossyhead/ds_bootcamp/GameExplorer/app/users_db/feedback.csv'
    try:
        with open(feedback_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

        updated = False
        for row in rows:
            if row['telegram_user_id'] == str(telegram_user_id) and row['user_input'] == user_input:
                row['game_name'] = recommendation['game_name']
                row['game_url'] = recommendation['game_url']
                row['game_release_date'] = recommendation['game_release_date']
                row['game_genres'] = recommendation['game_genres']
                row['game_id'] = recommendation['game_id']
                row['rating'] = rating
                updated = True
                break

        if not updated:
            print(f"Feedback for user {telegram_user_id} with input '{user_input}' not found.")
            return

        with open(feedback_file, mode='w', newline='', encoding='utf-8') as file:
            # writer = csv.writer(file)
            writer = csv.DictWriter(file, fieldnames=[
                'date', 'telegram_user_id', 'user_input', 'game_name', 'game_url', 
                'game_release_date', 'game_genres', 'game_id', 'rating'
            ])
            writer.writeheader()
            writer.writerows(rows)

    except Exception as e:
        print(f"Error updating feedback rating: {e}")