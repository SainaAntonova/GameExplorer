# GameExplorer


## About the Project

GameExplorer is a [Telegram bot](https://t.me/Game_Explorer_Bot) designed to search and recommend games and DLCs from Steam. The project is developed to help users discover new games based on their preferences, provide random game recommendations, and allow users to rate games.

## Key Features

- Text-Based Recommendations: Users can choose filters, and the bot will search for and recommend games based on the input text using natural language processing models.
- Random Game: The bot can suggest a random game or DLC from Steam.
- Game Rating: Users can rate the recommended games, which helps improve recommendations and track their preferences.
- Upcoming Games: Users can get new released games from Steam.
- Favorites: Users can add favorite games to their list and get it


## Main Commands

- /start: Start interacting with the bot.
- /help: Get a list of available commands.
- /info: Information about the project.
- /filters: Choose filters and enter text queries to receive 10 personalized game recommendations.
- /random: Get 1 a random game or DLC from SteamAPI.
- /upcoming: Get 3 new released games from SteamAPI.
- /favorites: Get your favorite list of apps.

## Technologies

- Python: The main programming language used for bot development.
- Aiogram: A library for creating Telegram bots.
- Sentence Transformers: A machine learning model for processing text queries.
- Chroma: A library for efficient similarity search and clustering of dense vectors.
- Pandas, Scikit-learn and Numpy: Libraries for data processing and analysis.
- Requests: A library for making HTTP requests to the Steam API.

## Project Structure

- main.py: The main file for starting the bot, setting up, and launching the command dispatcher.
- app/random_game_steam.py: Functions for getting random games and saving user ratings data.
- app/handlers.py: Handlers for commands and user interactions.
- app/keyboards.py: Creating keyboards and buttons for convenient user interaction.
- app/model.py: Functions for processing text queries and finding recommendations.
- app/feedback.py: To recieve feedback from users.
- app/users_db/favotites.csv: Data of user's favorite games
- app/users_db/feedback.csv: To collect recomendation ratings
- app/users_db/user_ratings.csv: To collect game ratings
- model/proj/: Embeddings, ChromaDB

## Contributors

- [SainaAntonova](https://github.com/SainaAntonova): Development of the main functionality of the bot.
- [Igor Svilanovich](https://github.com/svilanovich): Data processing and integration of machine learning models.





create .env:
BOT_TOKEN=
STEAM_API_KEY=

