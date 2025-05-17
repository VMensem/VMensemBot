from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_creator_keyboard() -> ReplyKeyboardMarkup:
    """Create creator keyboard with all commands including creator-only commands."""
    keyboard = [
        [
            KeyboardButton(text="/rules"),
            KeyboardButton(text="/rank"),
            KeyboardButton(text="/info")
        ],
        [
            KeyboardButton(text="/ap"),
            KeyboardButton(text="/staff"),
            KeyboardButton(text="/words")
        ],
        [
            KeyboardButton(text="/stats"),
            KeyboardButton(text="/addadmin"),
            KeyboardButton(text="/unadmin")
        ],
        [
            KeyboardButton(text="/help"),
            KeyboardButton(text="/id")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

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
            KeyboardButton(text="/staff"),
            KeyboardButton(text="/words")
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
            KeyboardButton(text="/staff"),
            KeyboardButton(text="/help"),
            KeyboardButton(text="/id")
        ],
        [
            KeyboardButton(text="/shop")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)