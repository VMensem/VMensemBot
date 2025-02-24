from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Create admin keyboard with common commands."""
    keyboard = [
        [
            KeyboardButton(text="/rules"),
            KeyboardButton(text="/rank"),
            KeyboardButton(text="/info")
        ],
        [
            KeyboardButton(text="/ap"),
            KeyboardButton(text="/stuff")
        ],
        [
            KeyboardButton(text="/help"),
            KeyboardButton(text="/id")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_user_keyboard() -> ReplyKeyboardMarkup:
    """Create user keyboard with basic commands."""
    keyboard = [
        [
            KeyboardButton(text="/rules"),
            KeyboardButton(text="/rank"),
            KeyboardButton(text="/info")
        ],
        [
            KeyboardButton(text="/help"),
            KeyboardButton(text="/id")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)