from typing import Final
import os

# Bot configuration
BOT_TOKEN: Final = os.environ.get("BOT_TOKEN")  # Token will be loaded from environment variables
CREATOR_ID: Final = 1951437901  # Creator's Telegram ID
CREATOR_USERNAME: Final = "@admin"  # Default admin username

# File paths
RULES_FILE: Final = "data/rules.json"
ADMINS_FILE: Final = "data/admins.json"
BANNED_WORDS_FILE: Final = "data/banned_words.json"

# Message templates
WELCOME_MESSAGE: Final = """
Добро пожаловать в Модерационного Бота!
Используйте /help чтобы увидеть доступные команды.
"""

HELP_MESSAGE: Final = """
<b>Доступные Команды:</b>

<b>Основные Команды:</b>
/start - Запустить бота
/help - Показать это сообщение помощи
/rules - Показать правила чата
/id - Показать ваш Telegram ID

<b>Команды Администратора:</b>
/setrules - Установить новые правила
/addword - Добавить запрещенное слово
/unword - Убрать запрещенное слово
/stuff - Показать статистику бота
/addadmin - Добавить нового администратора
/unadmin - Удалить администратора
"""