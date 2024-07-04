import re
import string
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from chromadb.utils.batch_utils import create_batches
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
import chromadb



# Загрузка модели и эмбедингов
description_embeddings = np.load('/Users/mossyhead/ds_bootcamp/GameExplorer/model/proj/description_embeddings.npy')
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
model.to('cpu')

# Понижаем размерность эмбедингов
lsa = make_pipeline(TruncatedSVD(n_components=128), Normalizer(copy=False))
fited_description_embeddings = lsa.fit_transform(description_embeddings)
explained_variance = lsa[0].explained_variance_ratio_.sum()
print(f"Explained variance of the SVD step: {explained_variance * 100:.1f}%")


fited_description_embeddings = fited_description_embeddings / np.linalg.norm(fited_description_embeddings, axis=1, keepdims=True)

final_df = pd.read_csv('/Users/mossyhead/ds_bootcamp/GameExplorer/model/proj/filter_df.csv') 
final_df = final_df.set_index('steam_appid')


# Подключение к ChromaDB и наполнение базы данных
# client = chromadb.PersistentClient(path="/Users/mossyhead/ds_bootcamp/GameExplorer/model/proj/chromadb.db")
# main_collection = client.get_collection("main_collection")
client = chromadb.Client()
main_collection = client.create_collection("main_collection")


stop_words = set(stopwords.words('russian') + stopwords.words('english'))
emoji_pattern = re.compile(
    "["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F700-\U0001F77F"  # alchemical symbols
    u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    u"\U0001FA00-\U0001FA6F"  # Chess Symbols
    u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    u"\U00002702-\U000027B0"  # Dingbats
    u"\U000024C2-\U0001F251" 
    "]+", flags=re.UNICODE)
pattern = r'&[a-zA-Z0-9#]+;'

# Функция для очистки текста перед созданием эмбеддингов
def clear_text(x):
    x = re.sub(re.compile('<.*?>'), ' ', x)
    x = emoji_pattern.sub(r'', x)
    x = re.sub(r'\r\n|\r|\n', '', x)
    x = re.sub(pattern, '', x)
    x = re.sub(r'http\S+', '', x)
    x = x.translate(str.maketrans('', '', string.punctuation))
    x = re.sub(' +', ' ', x)
    x = x.lower()
    x = ' '.join([i for i in x.split(' ') if i not in stop_words])
    return x
# Наполняем базу данных
ids = [str(game_id) for game_id in final_df.index]
embeddings = [embedding.tolist() for embedding in fited_description_embeddings]
metadatas = [
    {
        "steam_appid": game_id,
        "name": final_df.loc[game_id, 'name'],
        "single_player": int(final_df.loc[game_id, 'Для одного игрока']),
        "family_library": int(final_df.loc[game_id, 'Family Library Sharing']),
        "MMO": int(final_df.loc[game_id, 'MMO']),
        "action": int(final_df.loc[game_id, 'Экшены']),
        "indie": int(final_df.loc[game_id, 'Инди']),
        "simulator": int(final_df.loc[game_id, 'Симуляторы']),
        "strategy": int(final_df.loc[game_id, 'Стратегии']),
        "casual": int(final_df.loc[game_id, 'Казуальные игры']),
        "adventure": int(final_df.loc[game_id, 'Приключенческие игры']),
        "RPG": int(final_df.loc[game_id, 'Ролевые игры']),
        "VR": int(final_df.loc[game_id, 'VR']),
        "share/split_screen": int(final_df.loc[game_id, 'Share/Split Screen']),
        "f2p": int(final_df.loc[game_id, 'f2p']),
        "coop": int(final_df.loc[game_id, 'Co-op']),
        "multiplayer": int(final_df.loc[game_id, 'Multiplayer']),
        "racing/sport": int(final_df.loc[game_id, 'Racing/Sport']),
    }
    for game_id in final_df.index
]

batches = create_batches(api=client, ids=ids, embeddings=embeddings, metadatas=metadatas)

for batch in batches:
    main_collection.add(ids=batch[0], embeddings=batch[1], metadatas=batch[2])

# Функция, которая преобразует список пользовательских фильтров в нужный формат
# def make_fil(l):
#     conditions = [{field: {'$eq': 1}} for field in l]
#     return {'$and': conditions}
    
def make_fil(filters):
    if not filters:
        # Если фильтры пусты, используйте все фильтры
        filters = [
            'single_player', 'family_library', 'MMO', 'action', 'indie', 'simulator',
            'strategy', 'casual', 'adventure', 'RPG', 'VR', 'share/split_screen', 
            'f2p', 'coop', 'multiplayer', 'racing/sport'
        ]
    conditions = [{field: {'$eq': 1}} for field in filters]
    # if len(conditions) == 1:
    #     return conditions[0]  # Возвращаем одно условие
    # else:
    #     return {'$and': conditions}
    if len(conditions) == 1:
        return conditions[0]  # Возвращаем одно условие
    if len(conditions) == 1:
        return {conditions[0]: {'$eq': 1}} 

# Пользовательские фильтры и пользовательский запрос
def search(user_query, filters):
    user_query = clear_text(user_query)
    query_embedding = model.encode([user_query], convert_to_tensor=True).cpu().numpy()
    query_embedding = lsa.transform(query_embedding)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True) 
    results = main_collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=10,
        where=make_fil(filters)
    )
    result_ids = [int(x) for x in results['ids'][0]]
    result_metadatas = results['metadatas'][0]
    recommended_games = [meta for meta in result_metadatas if int(meta['steam_appid']) in result_ids]
    return recommended_games
                                                       
