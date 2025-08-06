import os
import logging
from typing import Final, Optional

# Telegram Bot Configuration
BOT_TOKEN: Final = os.environ.get("BOT_TOKEN")
CREATOR_ID: Final = 1951437901
CREATOR_USERNAME: Final = "@vladlotto"
MANAGEMENT_CHAT_ID: Final = -1002473077041

# Discord Bot Configuration  
DISCORD_TOKEN: Final = os.getenv('DISCORD_TOKEN', '')
DISCORD_APPLICATION_ID: Final = os.getenv('DISCORD_APPLICATION_ID', '')
DISCORD_PUBLIC_KEY: Final = os.getenv('DISCORD_PUBLIC_KEY', '')
DISCORD_USE_INTERACTIONS: Final = os.getenv('DISCORD_USE_INTERACTIONS', 'true').lower() == 'true'

# Arizona RP API Configuration
API_KEY: Final = os.getenv('API_KEY', '')
API_URL: Final = os.getenv('API_URL', 'https://api.depscian.tech/v2/player/find')

# Bot Settings
DISCORD_COMMAND_PREFIX: Final = os.getenv('DISCORD_COMMAND_PREFIX', '!')
REQUEST_TIMEOUT: Final = int(os.getenv('REQUEST_TIMEOUT', '30'))

# File paths
RULES_FILE: Final = "data/rules.json"
ADMINS_FILE: Final = "data/admins.json"
BANNED_WORDS_FILE: Final = "data/banned_words.json"
INFO_FILE: Final = "data/info.json"
RANK_FILE: Final = "data/rank.json"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def validate_config() -> bool:
    """Validate that all required configuration is present"""
    required_vars = [
        ("BOT_TOKEN", BOT_TOKEN),
    ]
    
    optional_vars = [
        ("DISCORD_TOKEN", DISCORD_TOKEN),
        ("API_KEY", API_KEY),
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        logger.error(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
        return False
    
    missing_optional = []
    for var_name, var_value in optional_vars:
        if not var_value:
            missing_optional.append(var_name)
    
    if missing_optional:
        logger.warning(f"Отсутствуют опциональные переменные окружения: {', '.join(missing_optional)}")
        logger.info("Бот будет работать только с доступными платформами")
    
    return True

# Message templates for Telegram
WELCOME_MESSAGE: Final = """
👋 Добро пожаловать в MensemBot!

🤖 Я помогу вам с управлением чатом и предоставлю полезную информацию.

🎮 Новая функция: проверка статистики игроков Arizona RP!

Вся информация в /info
Чат Mensem Family - https://t.me/mensemsamp
"""

HELP_MESSAGE: Final = """
<b>Доступные Команды:</b>

👥 Общие команды:
/start - Запустить бота
/help - Показать это сообщение помощи
/rules - Показать правила чата
/rank - Показать информацию о рангах
/info - Показать информацию
/staff - Показать информацию о персонале
/id - Показать ваш Telegram ID
/shop - Подать заявку (только в ЛС с ботом)

🎮 Arizona RP команды:
/stats &lt;ник&gt; &lt;ID сервера&gt; - Статистика игрока
/servers - Показать все серверы Arizona RP

⚙️ Команды администратора:
/setrules - Изменить правила чата
/setinfo - Изменить информацию 
/setrank - Изменить информацию о рангах
/addword - Добавить запрещенное слово
/unword - Убрать запрещенное слово
/words - Показать список запрещенных слов
/botstats - Статистика бота (только для создателя)
/addadmin - Добавить админа
/unadmin - Удалить админа
"""

ADMIN_PANEL_MESSAGE: Final = """
<b>Админ-панель</b>

Доступные команды администратора:
/setrules - Изменить правила чата
/setinfo - Изменить информацию 
/setrank - Изменить информацию о рангах
/addword - Добавить запрещенное слово
/unword - Убрать запрещенное слово
/words - Показать список запрещенных слов
/botstats - Статистика бота (только для создателя)
/addadmin - Добавить админа
/unadmin - Удалить админа
"""

RANK_MESSAGE: Final = """
💰Как получить ранг?💵
2 ранг — вступить в @mensemsamp
3 ранг — 750к
4 ранг — 1кк
5 ранг — 1.5кк
6 ранг — 2кк
7 ранг — 3кк
8 ранг — 4кк - ✏️Имя_Mensem/Имя_Barone
"""

WORDS_MESSAGE: Final = """
<b>Список запрещенных слов:</b>
{
"""

SHOP_HELP_MESSAGE: Final = """
Для подачи заявки, пожалуйста:
1. Отправьте фото или видео
2. В подписи к медиафайлу укажите:
Ник:
Ранг:
Доказательства:

Пример:
[Фото/Видео]
Ник: Vlad_Mensem
Ранг: 5
Доказательства: Скриншот пополнения семейного счёта
"""

# Command descriptions for BotFather menu
COMMAND_DESCRIPTIONS = {
    "start": "Главное меню бота",
    "help": "Показать список команд", 
    "rules": "Правила чата",
    "info": "Информация о сервере",
    "rank": "Рейтинг участников",
    "staff": "Список администрации",
    "id": "Показать ваш ID",
    "shop": "Подать заявку в магазин",
    "stats": "Статистика игрока Arizona RP",
    "servers": "Показать серверы Arizona RP",
    "setrules": "Изменить правила (только админы)",
    "setinfo": "Изменить информацию (только админы)",
    "setrank": "Изменить рейтинг (только админы)",
    "addword": "Добавить запрещенное слово (только админы)",
    "unword": "Удалить запрещенное слово (только админы)",
    "words": "Показать запрещенные слова (только админы)",
    "addadmin": "Добавить администратора (только создатель)",
    "unadmin": "Удалить администратора (только создатель)",
    "botstats": "Статистика работы бота (только создатель)"
}