import os
import requests
from bs4 import BeautifulSoup


def get_upcoming_games():
    url = 'https://store.steampowered.com/search/?supportedlang=russian&filter=comingsoon&ndl=1' # язык ставим русский по умолчанию 
    try:
        response = requests.get(url)
        if response.status_code == 200:
            upcoming_games = []

            soup = BeautifulSoup(response.text, 'html.parser')
            game_items = soup.find_all('a', class_='search_result_row')

            for item in game_items[:3]:  # Берем первые три игры для примера
                game_name = item.find('span', class_='title').text.strip()
                release_date= item.find('div', class_='search_released').text.strip()
                store_link = item.get('href')

                game_page = requests.get(store_link)
                if game_page.status_code == 200:
                    game_soup = BeautifulSoup(game_page.text, 'html.parser')
                    genre_tags = game_soup.find('div', id='genresAndManufacturer').find_all('a')
                    genres = [tag.text.strip() for tag in genre_tags if '/genre/' in tag['href']]
                
                    # Remove duplicates from genres
                    genres = list(set(genres))
                    # Extracting OS info (if available)
                    os_tags = game_soup.find_all('span', class_='platform_img')
                    os_info = [os_tag['class'][1] for os_tag in os_tags if 'platform_img' in os_tag['class']]


                    upcoming_games.append({
                        'name': game_name,
                        'release_date': release_date,
                        'store_link': store_link,
                        'genre': genres,
                        'os': os_info
                    })

                    print(f"Found upcoming game: {game_name} (Release Date: {release_date}) - {store_link}")

            return upcoming_games
        else:
            print(f"Failed to retrieve data: {response.status_code} - {response.reason}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching upcoming games: {e}")
        return None
    except Exception as ex:
        print(f"Error: {ex}")
        return None

