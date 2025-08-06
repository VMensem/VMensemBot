# 🚀 Полное руководство по развертыванию MensemBot

## 📋 Подготовка к развертыванию

### 1. Загрузка на GitHub

```bash
# Создайте новый репозиторий на GitHub (например: MensemBot)
# Затем выполните:

git init
git add .
git commit -m "Initial commit: MensemBot unified multi-platform bot"
git branch -M main
git remote add origin https://github.com/ВАШ_USERNAME/MensemBot.git
git push -u origin main
```

### 2. Настройка Discord Application

1. Перейдите на [Discord Developer Portal](https://discord.com/developers/applications)
2. Создайте новое приложение "MensemBot"
3. Перейдите в раздел "Bot" и создайте бота
4. Скопируйте следующие данные:
   - **Application ID** (из General Information)
   - **Public Key** (из General Information) 
   - **Bot Token** (из Bot, опционально)

## 🌐 Развертывание на Render.com

### Шаг 1: Создание сервиса
1. Перейдите на [render.com](https://render.com)
2. Зарегистрируйтесь и войдите в аккаунт
3. Нажмите "New" → "Web Service"
4. Подключите ваш GitHub репозиторий

### Шаг 2: Настройка сервиса
- **Name**: `mensembot` (или любое другое имя)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r render_requirements.txt`
- **Start Command**: `python render_bot.py`
- **Plan**: `Free` (или любой другой)

### Шаг 3: Environment Variables
Добавьте следующие переменные окружения:

| Переменная | Значение | Обязательная |
|-----------|----------|--------------|
| `BOT_TOKEN` | Ваш Telegram Bot Token | ✅ |
| `DISCORD_APPLICATION_ID` | Discord Application ID | ❌ |
| `DISCORD_PUBLIC_KEY` | Discord Public Key | ❌ |
| `DISCORD_USE_INTERACTIONS` | `true` | ❌ |
| `API_KEY` | Arizona RP API Key | ❌ |
| `PYTHON_VERSION` | `3.11.10` | ❌ |

### Шаг 4: Deploy
Нажмите "Create Web Service" - развертывание начнется автоматически.

## 🎮 Настройка Discord Interactions

После успешного развертывания на Render:

1. Скопируйте URL вашего приложения (например: `https://mensembot-xxxx.onrender.com`)
2. В Discord Developer Portal перейдите в "General Information"
3. В поле "Interactions Endpoint URL" введите:
   ```
   https://ваше-приложение.onrender.com/discord/interactions
   ```
4. Сохраните настройки

Discord автоматически отправит ping запрос для проверки endpoint.

## 🔍 Проверка работы

### Проверка сервисов:
- **Главная страница**: `https://ваше-приложение.onrender.com/`
- **Health check**: `https://ваше-приложение.onrender.com/health`
- **Discord webhook**: `https://ваше-приложение.onrender.com/discord/interactions`

### Тестирование ботов:
1. **Telegram**: Найдите @mensembot и отправьте `/help`
2. **Discord**: Пригласите бота на сервер и используйте `/help`

## ⚡ Альтернативные платформы

### Railway.app
```bash
# Установите Railway CLI
npm install -g @railway/cli

# Войдите в аккаунт
railway login

# Создайте новый проект
railway init
railway add

# Добавьте переменные окружения
railway variables set BOT_TOKEN=ваш_токен
railway variables set DISCORD_APPLICATION_ID=ваш_id

# Deploy
railway up
```

### Heroku
```bash
# Создайте приложение
heroku create ваше-приложение

# Добавьте переменные
heroku config:set BOT_TOKEN=ваш_токен
heroku config:set DISCORD_APPLICATION_ID=ваш_id
heroku config:set DISCORD_PUBLIC_KEY=ваш_ключ

# Deploy
git push heroku main
```

### Fly.io
```bash
# Установите flyctl
# https://fly.io/docs/hands-on/install-flyctl/

# Создайте приложение
flyctl launch

# Добавьте переменные
flyctl secrets set BOT_TOKEN=ваш_токен
flyctl secrets set DISCORD_APPLICATION_ID=ваш_id

# Deploy
flyctl deploy
```

## 🛠️ Troubleshooting

### Общие проблемы:

1. **Бот не отвечает на команды:**
   - Проверьте переменные окружения
   - Убедитесь что BOT_TOKEN правильный
   - Проверьте логи сервиса

2. **Discord Interactions не работают:**
   - Проверьте Discord Developer Portal настройки
   - Убедитесь что endpoint URL правильный
   - Проверьте DISCORD_APPLICATION_ID и DISCORD_PUBLIC_KEY

3. **Сервис падает при запуске:**
   - Проверьте логи в Render Dashboard
   - Убедитесь что все зависимости установлены
   - Проверьте Python версию

### Логи и мониторинг:
- **Render.com**: Dashboard → Logs
- **Railway**: `railway logs`
- **Heroku**: `heroku logs --tail`

## 🎉 Готово!

Ваш MensemBot теперь работает 24/7 на облачной платформе с поддержкой:
- ✅ Telegram команды
- ✅ Discord slash команды  
- ✅ Arizona RP статистика
- ✅ Модерация чатов
- ✅ Автоматические перезапуски
- ✅ Health monitoring

**URL Discord Interactions**: `https://ваше-приложение.onrender.com/discord/interactions`
**Health Check**: `https://ваше-приложение.onrender.com/health`