# MensemBot - Unified Multi-Platform Bot

Объединенный бот для Telegram и Discord с поддержкой модерации сообщества и статистики Arizona RP.

## 🚀 Особенности

- **Мультиплатформенность**: Работает одновременно в Telegram и Discord
- **Модерация**: Фильтр запрещенных слов, управление правилами, роли админов
- **Arizona RP**: Статистика игроков через Deps API
- **24/7 Режим**: Круглосуточная работа с поддержкой keep-alive
- **Discord Interactions**: Поддержка slash команд через HTTP webhook

## 📋 Команды

### Основные
- `/help` - Список команд
- `/rules` - Правила сервера
- `/info` - Информация
- `/rank` - Система рангов
- `/id` - Получить ваш ID

### Arizona RP
- `/stats <ник> <сервер>` - Статистика игрока
- `/servers` - Список серверов

### Админские
- `/setrules` - Установить правила
- `/setinfo` - Установить информацию
- `/setrank` - Установить ранги
- `/addword` / `/unword` - Управление запрещенными словами
- `/addadmin` / `/unadmin` - Управление администраторами

## 🔧 Развертывание

### Локально
```bash
git clone https://github.com/ваш-username/MensemBot.git
cd MensemBot
pip install -r render_requirements.txt
python bot.py
```

### Render.com
1. Форкните репозиторий на GitHub
2. Создайте новый Web Service на Render.com
3. Подключите ваш GitHub репозиторий
4. Настройте переменные окружения:
   - `BOT_TOKEN` - Telegram Bot Token
   - `DISCORD_TOKEN` - Discord Bot Token (опционально)
   - `DISCORD_APPLICATION_ID` - Discord Application ID
   - `DISCORD_PUBLIC_KEY` - Discord Public Key
   - `API_KEY` - Arizona RP API Key (опционально)
5. Deploy!

### Heroku
```bash
git clone https://github.com/ваш-username/MensemBot.git
cd MensemBot
heroku create ваше-приложение
heroku config:set BOT_TOKEN=ваш_токен
heroku config:set DISCORD_APPLICATION_ID=ваш_id
heroku config:set DISCORD_PUBLIC_KEY=ваш_ключ
git push heroku main
```

## ⚙️ Настройка Discord Interactions

1. Перейдите в [Discord Developer Portal](https://discord.com/developers/applications)
2. Создайте новое приложение или выберите существующее
3. В разделе "General Information":
   - Скопируйте **Application ID**
   - Скопируйте **Public Key**
4. В поле "Interactions Endpoint URL" введите:
   ```
   https://ваше-приложение.onrender.com/discord/interactions
   ```
5. Сохраните настройки

## 🔑 Переменные окружения

| Переменная | Описание | Обязательная |
|-----------|----------|--------------|
| `BOT_TOKEN` | Telegram Bot Token | ✅ |
| `DISCORD_TOKEN` | Discord Bot Token | ❌ |
| `DISCORD_APPLICATION_ID` | Discord Application ID | ❌ |
| `DISCORD_PUBLIC_KEY` | Discord Public Key | ❌ |
| `DISCORD_USE_INTERACTIONS` | Использовать Interactions (true/false) | ❌ |
| `API_KEY` | Arizona RP API Key | ❌ |

## 📁 Структура проекта

```
MensemBot/
├── bot.py                  # Основной файл запуска
├── unified_bot.py          # Telegram bot логика
├── discord_bot.py          # Discord bot логика
├── discord_interactions.py # Discord Interactions handler
├── unified_config.py       # Конфигурация
├── data_manager.py         # Управление данными
├── arizona_api.py          # Arizona RP API
├── filters.py              # Фильтры для команд
├── keep_alive.py          # Flask server для 24/7
├── data/                   # JSON файлы с данными
│   ├── rules.json
│   ├── admins.json
│   ├── banned_words.json
│   ├── info.json
│   └── rank.json
├── render_requirements.txt # Зависимости для Render
├── Procfile               # Настройки для Heroku
├── wsgi.py               # WSGI entry point
├── runtime.txt           # Версия Python
└── README.md            # Документация
```

## 🛠️ Технологии

- **Python 3.11**
- **aiogram** - Telegram Bot API
- **discord.py** - Discord API
- **Flask** - Web сервер
- **aiohttp** - HTTP клиент
- **JSON** - Хранение данных

## 📞 Поддержка

Создатель: @vladlotto
Telegram бот: @mensembot

## 📄 Лицензия

MIT License - используйте как хотите!

---

💝 **Сделано с любовью для сообщества Mensem Family**