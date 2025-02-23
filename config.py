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
INFO_FILE: Final = "data/info.json"
SCRIPTS_FILE: Final = "data/scripts.json"

# Message templates
WELCOME_MESSAGE: Final = """
Добро пожаловать в Модерационного Бота!
Используйте /help чтобы увидеть доступные команды.
"""

HELP_MESSAGE: Final = """
<b>Доступные Команды:</b>

/start - Запустить бота
/help - Показать это сообщение помощи
/rules - Показать правила чата
/rank - Показать информацию о рангах
/info - Показать информацию
/scripts - Показать список скриптов
/id - Показать ваш Telegram ID
/staff - Показать информацию о персонале
"""

ADMIN_PANEL_MESSAGE: Final = """
<b>Админ-панель</b>

Доступные команды администратора:
/setrules - Изменить правила
/setinfo - Изменить информацию
/setrank - Изменить информацию о рангах
/addscript - Добавить скрипт
/removescript - Удалить скрипт
/addword - Добавить запрещенное слово
/unword - Убрать запрещенное слово
/stuff - Статистика бота
/addadmin - Добавить админа
/unadmin - Удалить админа
"""

RANK_MESSAGE: Final = """
Как получить ранги?
2 ранг — вступить в нашу группу ТГ
3 ранг — 750к
4 ранг — 1кк
5 ранг — 1.5кк
6 ранг — 2кк
7 ранг — 3кк
8 ранг — 4кк
"""