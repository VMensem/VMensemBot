from typing import Final
import os

# Bot configuration
BOT_TOKEN: Final = os.environ.get("BOT_TOKEN")  # Token will be loaded from environment variables
CREATOR_ID: Final = 1951437901  # Creator's Telegram ID
CREATOR_USERNAME: Final = "@vladlotto"  # Creator's username
MANAGEMENT_CHAT_ID: Final = -1002473077041  # Chat ID for management group (converted from 2473077041)

# File paths
RULES_FILE: Final = "data/rules.json"
ADMINS_FILE: Final = "data/admins.json"
BANNED_WORDS_FILE: Final = "data/banned_words.json"
INFO_FILE: Final = "data/info.json"
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
/staff - Показать информацию о персонале
/shop - Подать заявку (только в ЛС с ботом)
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
/words - Показать список запрещенных слов
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

WORDS_MESSAGE: Final = """
<b>Список запрещенных слов:</b>
{}
"""

SHOP_HELP_MESSAGE: Final = """
Для подачи заявки, пожалуйста:
1. Отправьте фото или видео вашего персонажа
2. В подписи к медиафайлу укажите:
Ник:
Ранг:
Доказательства:

Пример:
[Фото/Видео]
Ник: Vlad_Mensem
Ранг: 5
Доказательства: Скриншот пополнения фам счёта
"""