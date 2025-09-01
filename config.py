from typing import Final
import os

# Bot configuration
BOT_TOKEN: Final = os.environ.get("BOT_TOKEN")  # Token will be loaded from environment variables
CREATOR_ID: Final = 1951437901  # Creator's Telegram ID
CREATOR_USERNAME: Final = "@vladlotto"  # Creator's username
MANAGEMENT_CHAT_ID: Final = -1002473077041  # Chat ID for management group (converted from 2473077041)

# File paths
RULES_FILE: Final = "data/rules.json"
RANK_FILE: Final = "data/rank.json"
ADMINS_FILE: Final = "data/admins.json"
BANNED_WORDS_FILE: Final = "data/banned_words.json"
INFO_FILE: Final = "data/info.json"

# Message templates
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
/stats - Статистика бота (только для создателя)
/addadmin - Добавить админа
/unadmin - Удалить админа
"""

RANK_MESSAGE: Final = RANK_FILE

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
