from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/start"),
            KeyboardButton(text="/help"),
            KeyboardButton(text="/info"),
        ],
        [
            KeyboardButton(text="/filters"),
            KeyboardButton(text="/random"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Choose option...'
)

next_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Next", callback_data="next"),
        ],
    ]
)
def create_rating_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(1,6):
        keyboard.insert(InlineKeyboardButton(text=str(i), callback_data=f'rate_{i}'))
    return keyboard

def create_initial_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    rate_button = InlineKeyboardButton(text="Rate this app", callback_data="rate")
    next_button = InlineKeyboardButton(text="Next app", callback_data="next")
    keyboard.add(rate_button, next_button)
    return keyboard

# Функция для создания клавиатуры фильтров
def filter_keyboard(filter_type):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if filter_type == "os":
        keyboard.add(
            InlineKeyboardButton("Mac", callback_data="os_mac"),
            InlineKeyboardButton("Linux", callback_data="os_linux"),
            InlineKeyboardButton("Windows", callback_data="os_windows"),
            InlineKeyboardButton("Do not choose filter", callback_data="os_none")
        )
    elif filter_type == "genre":
        keyboard.add(
            InlineKeyboardButton("Action", callback_data="genre_action"),
            InlineKeyboardButton("Adventure", callback_data="genre_adventure"),
            InlineKeyboardButton("Indie", callback_data="genre_indie"),
            InlineKeyboardButton("Do not choose filter", callback_data="os_none")
            # Добавьте другие жанры по аналогии
        )
    return keyboard