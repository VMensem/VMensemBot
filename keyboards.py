from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Create admin keyboard with common commands."""
    keyboard = [
        [
            KeyboardButton(text="/rules"),
            KeyboardButton(text="/setrules"),
            KeyboardButton(text="/stuff")
        ],
        [
            KeyboardButton(text="/addword"),
            KeyboardButton(text="/unword"),
            KeyboardButton(text="/id")
        ],
        [
            KeyboardButton(text="/addadmin"),
            KeyboardButton(text="/unadmin"),
            KeyboardButton(text="/help")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_user_keyboard() -> ReplyKeyboardMarkup:
    """Create user keyboard with basic commands."""
    keyboard = [
        [
            KeyboardButton(text="/rules"),
            KeyboardButton(text="/help"),
            KeyboardButton(text="/id")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)