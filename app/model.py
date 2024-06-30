import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

import pandas as pd
from aiogram import types
from aiogram.types import ParseMode

# Загрузка моделей и данных
index_file = '/Users/mossyhead/ds_bootcamp/GameExplorer/model/description_embeddings_3.index'
model_file = '/Users/mossyhead/ds_bootcamp/GameExplorer/model/paraphrase-multilingual-MiniLM-L12-v2_3.pth'
embeddings_file = '/Users/mossyhead/ds_bootcamp/GameExplorer/model/description_embeddings_3.npy'
cropped_df = pd.read_csv('/Users/mossyhead/ds_bootcamp/GameExplorer/steam_data/csv_files/games_2024_cleaned.csv')

device = 'cuda' if torch.cuda.is_available() else 'cpu'

index = faiss.read_index(index_file)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
model.load_state_dict(torch.load(model_file))
description_embeddings_np = np.load(embeddings_file)


# Функция для обработки пользовательского ввода

# def process_filters(user_input):
#     user_input = user_input.strip()
#     # Кодирование вектора для пользовательского ввода
#     user_embedding = model.encode([user_input], convert_to_tensor=True)
#     # Вычисление косинусного сходства с описаниями игр
#     _, indices = index.search(user_embedding.cpu().numpy(), 10)
#     recommendations = []
#     # Вывод рекомендаций игр
#     for idx in indices[0]:
#         game_name = cropped_df.loc[idx, 'name']
#         # game_type = cropped_df.loc[idx, 'type']
#         game_id = cropped_df.loc[idx, 'AppID']
#         release_date = cropped_df.loc[idx, 'release_date']
            
#         game_info = (
#                 f'<b>{game_name}</b>\n\n'
#                 # f'Type: {game_type}\n'
#                 f'Дата выхода: {release_date}\n'
#                 f'AppID: {game_id}\n'
#                 f'Жми для перехода на страницу в Steam: '
#                 f'http://store.steampowered.com/app/{game_id}'
#         )
#         recommendations.append(game_info)

#     return recommendations
#     # return game_info

def process_filters(user_input, os_filter=None, genre_filter=None):
    user_input = user_input.strip()
    
    # Применение фильтров по выбранной операционной системе и жанру
    filtered_df = cropped_df.copy()
    if os_filter:
        filtered_df = filtered_df[filtered_df[os_filter] == True]
    if genre_filter:
        filtered_df = filtered_df[filtered_df['genres'].apply(lambda genres: genre_filter in genres)]
    # Кодирование вектора для пользовательского ввода
    user_embedding = model.encode([user_input], convert_to_tensor=True)
        
    # Вычисление косинусного сходства с описаниями игр
    _, indices = index.search(user_embedding.cpu().numpy(), 10)
        
    # Вывод рекомендаций игр
    recommendations = []
    for idx in indices[0]:
        if idx >= len(filtered_df):
            continue


        # здесь нужно обучить модель на df по genres, os и прочее 
            
        game_name = filtered_df.loc[idx, 'name']
        game_release_date = filtered_df.loc[idx, 'release_date']
        game_id = filtered_df.loc[idx, 'AppID']
            
        game_info = (
            f'<b>{game_name}</b>\n\n'
            f'Дата выхода: {game_release_date}\n'
            f'AppID: {game_id}\n'
            f'Жми для перехода на страницу в Steam: '
            f'http://store.steampowered.com/app/{game_id}\n\n'
        )
        recommendations.append(game_info)
    if len(recommendations) < 10:
        recommendations.append("Sorry")
    
    return recommendations
