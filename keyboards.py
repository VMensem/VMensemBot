from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Create admin keyboard with common commands."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("/rules"),
        KeyboardButton("/setrules"),
        KeyboardButton("/stuff")
    )
    keyboard.add(
        KeyboardButton("/addword"),
        KeyboardButton("/unword"),
        KeyboardButton("/id")
    )
    keyboard.add(
        KeyboardButton("/addadmin"),
        KeyboardButton("/unadmin"),
        KeyboardButton("/help")
    )
    return keyboard

def get_user_keyboard() -> ReplyKeyboardMarkup:
    """Create user keyboard with basic commands."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("/rules"),
        KeyboardButton("/help"),
        KeyboardButton("/id")
    )
    return keyboard
