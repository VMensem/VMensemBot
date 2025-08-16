import os
import logging
from typing import Final, Optional

# Telegram Bot Configuration
_bot_token = os.environ.get("BOT_TOKEN")
BOT_TOKEN: Final = _bot_token.strip() if _bot_token else None
CREATOR_ID: Final = 1951437901
CREATOR_USERNAME: Final = "@vladlotto"
MANAGEMENT_CHAT_ID: Final = -1002473077041

# Discord Bot Configuration  
_discord_token = os.getenv('DISCORD_TOKEN', '')
DISCORD_TOKEN: Final = _discord_token.strip() if _discord_token else ''
DISCORD_APPLICATION_ID: Final = os.getenv('DISCORD_APPLICATION_ID', '')
DISCORD_PUBLIC_KEY: Final = os.getenv('DISCORD_PUBLIC_KEY', '')
DISCORD_USE_INTERACTIONS: Final = os.getenv('DISCORD_USE_INTERACTIONS', 'true').lower() == 'true'

# Arizona RP API Configuration
_api_key = os.getenv('API_KEY', '')
API_KEY: Final = _api_key.strip() if _api_key else ''
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
Чат Mensem Family - https://t.me/+sl5f-AkJBmFiZjgy
"""

HELP_MESSAGE_USER: Final = """
<b>Доступные Команды:</b>

<b>👥 Общие команды:</b>
/start - Запустить бота
/help - Показать это сообщение помощи
/rules - Показать правила чата
/rank - Показать информацию о рангах
/info - Показать информацию
/staff - Показать список администрации
/id - Показать ваш Telegram ID
/shop - Подать заявку (только в ЛС с ботом)
/idea - Отправить идею руководству семьи

🎮 Arizona RP команды:
/stats &lt;Nick_Name&gt; &lt;ID сервера&gt; - Статистика игрока
/servers - Показать все серверы Arizona RP
"""

HELP_MESSAGE_ADMIN: Final = HELP_MESSAGE_USER + """
<b>⚙️ Команды администратора:</b>
/setrules - Изменить правила чата
/setinfo - Изменить информацию 
/setrank - Изменить информацию о рангах
/addword - Добавить запрещенное слово
/unword - Убрать запрещенное слово
/words - Показать список запрещенных слов
"""

HELP_MESSAGE_CREATOR: Final = HELP_MESSAGE_ADMIN + """
<b>⚠️ Команды Создателя</b>
/botstats - Статистика бота
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
"""

RANK_MESSAGE: Final = """
💰Как получить ранг?💵
2 ранг — вступить в телеграм семьи
3 ранг — 750к
4 ранг — 1кк
5 ранг — 1.5кк
6 ранг — 2кк
7 ранг — 3кк
8 ранг — 4кк - ✏️Имя_Mensem
"""

WORDS_MESSAGE: Final = """
<b> Список запрещенных слов:</b>
{
"""

SHOP_HELP_MESSAGE: Final = """
⭐ <b>Подача заявки на ранг</b>

Для подачи заявки:
1. Отправьте фото или видео доказательств
2. В подписи к медиафайлу укажите:

Ник: ваш игровой ник
Ранг: на какой ранг претендуете  
Доказательства: описание прикрепленных доказательств

<b>Пример:</b>
[Фото/Видео]
Ник: Vlad_Mensem
Ранг: 5
Доказательства: Скриншот пополнения семейного счёта на 1.5кк
"""

# Command descriptions for BotFather menu
COMMAND_DESCRIPTIONS = {
    "start": "Запуск бота",
    "help": "Команды", 
    "rules": "Правила",
    "info": "Информация",
    "rank": "Цены на ранги",
    "staff": "Список администрации",
    "idea": "Отправить идею руководству семьи",
    "id": "Показать ваш Телеграм ID",
    "shop": "Подать заявку на ранг",
    "stats": "Статистика игрока Arizona RP",
    "servers": "Показать серверы Arizona RP"
}
