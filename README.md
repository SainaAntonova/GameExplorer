# GameExplorer


## About the Project

GameExplorer is a [Telegram bot](https://t.me/Game_Explorer_Bot) designed to search and recommend games and DLCs from Steam. The project is developed to help users discover new games based on their preferences, provide random game recommendations, and allow users to rate games.

## Key Features

- Text-Based Recommendations: Users can input text queries, and the bot will search for and recommend games based on the input text using natural language processing models.
- Random Game: The bot can suggest a random game or DLC from Steam.
- Game Rating: Users can rate the recommended games, which helps improve recommendations and track their preferences.


## Main Commands

- /start: Start interacting with the bot.
- /help: Get a list of available commands.
- /info: Information about the project.
- /filters: Enter text queries to receive personalized game recommendations.
- /random: Get a random game or DLC.

## Technologies

- Python: The main programming language used for bot development.
- Aiogram: A library for creating Telegram bots.
- Sentence Transformers: A machine learning model for processing text queries.
- Chroma: A library for efficient similarity search and clustering of dense vectors.
- Pandas and Numpy: Libraries for data processing and analysis.
- Requests: A library for making HTTP requests to the Steam API.

## Project Structure

- main.py: The main file for starting the bot, setting up, and launching the command dispatcher.
- app/random_game_steam.py: Functions for getting random games and saving user ratings data.
- app/handlers.py: Handlers for commands and user interactions.
- app/keyboards.py: Creating keyboards and buttons for convenient user interaction.
- app/model.py: Functions for processing text queries and finding recommendations.

## Contributors

- [SainaAntonova](https://github.com/SainaAntonova): Development of the main functionality of the bot.
- [Igor Svilanovich](https://github.com/svilanovich): Data processing and integration of machine learning models.

