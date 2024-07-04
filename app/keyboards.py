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
            KeyboardButton(text="/upcoming"),
        ],
        [
            KeyboardButton(text="/favorites"),
        ]
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
    keyboard.add(InlineKeyboardButton(text="Please, rate this game", callback_data="noop"))
    rating_buttons = [InlineKeyboardButton(text=str(i), callback_data=f'rate_{i}') for i in range(1, 6)]
    keyboard.add(*rating_buttons)
    return keyboard


def feedback_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=5)
    keyboard.add(InlineKeyboardButton(text="Please rate these recommendations", callback_data="noop"))
    feedback_buttons = [InlineKeyboardButton(text=f"{i} ⭐", callback_data=f'feedback_{i}') for i in range(1, 6)]
    keyboard.add(*feedback_buttons)
    return keyboard

def create_initial_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    rate_button = InlineKeyboardButton(text="Rate this app", callback_data="rate")
    next_button = InlineKeyboardButton(text="Next app", callback_data="next")
    favorite_button = InlineKeyboardButton(text="Add to favorites", callback_data="addfav_")
    keyboard.add(rate_button, next_button, favorite_button)
    return keyboard


# Function to create filters keyboard
def get_filter_keyboard(user_filters):
    filters = [
        'single_player', 'family_library', 'MMO', 'action', 'indie', 'simulator',
        'strategy', 'casual', 'adventure', 'RPG', 'VR', 'share/split_screen', 
        'f2p', 'coop', 'multiplayer', 'racing/sport'
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    for filter in filters:
        status = "✅" if filter in user_filters else ""
        keyboard.insert(InlineKeyboardButton(f"{filter} {status}", callback_data=f"filter_{filter}"))
    keyboard.add(InlineKeyboardButton('Reset', callback_data='reset_filters'))
    keyboard.add(InlineKeyboardButton('Done', callback_data='done_filters'))
    return keyboard