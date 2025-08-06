#!/bin/bash

# Скрипт автоматического развертывания MensemBot на GitHub + Render.com

echo "🚀 Подготовка MensemBot для развертывания..."

# Создание git репозитория если не существует
if [ ! -d ".git" ]; then
    echo "📁 Инициализация Git репозитория..."
    git init
    git add .
    git commit -m "Initial commit: MensemBot unified multi-platform bot"
fi

echo "📋 Проверка файлов для развертывания..."

# Проверка наличия необходимых файлов
files=(
    "bot.py"
    "unified_bot.py" 
    "discord_bot.py"
    "unified_config.py"
    "data_manager.py"
    "arizona_api.py"
    "filters.py"
    "keep_alive.py"
    "render_requirements.txt"
    "Procfile"
    "wsgi.py"
    "runtime.txt"
    "README.md"
)

missing_files=()
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Отсутствуют файлы: ${missing_files[*]}"
    echo "Пожалуйста, убедитесь что все файлы присутствуют перед развертыванием"
    exit 1
fi

echo "✅ Все необходимые файлы присутствуют"

# Создание директории data если не существует
if [ ! -d "data" ]; then
    echo "📁 Создание директории data..."
    mkdir -p data
    
    # Создание базовых JSON файлов
    echo '{"rules": "Правила пока не установлены."}' > data/rules.json
    echo '{"admins": []}' > data/admins.json
    echo '{"words": []}' > data/banned_words.json
    echo '{"info": "Информация пока не установлена."}' > data/info.json
    echo '{"rank_message": "Информация о рангах пока не установлена."}' > data/rank.json
fi

echo "📝 Инструкции по развертыванию:"
echo ""
echo "1. 🐱 GitHub:"
echo "   - Создайте репозиторий на GitHub"
echo "   - git remote add origin https://github.com/ваш-username/MensemBot.git"
echo "   - git push -u origin main"
echo ""
echo "2. 🌐 Render.com:"
echo "   - Перейдите на https://render.com"
echo "   - Создайте новый Web Service"
echo "   - Подключите ваш GitHub репозиторий"
echo "   - Build Command: pip install -r render_requirements.txt"
echo "   - Start Command: python bot.py"
echo ""
echo "3. 🔑 Environment Variables в Render:"
echo "   BOT_TOKEN=ваш_telegram_token"
echo "   DISCORD_APPLICATION_ID=ваш_discord_app_id"
echo "   DISCORD_PUBLIC_KEY=ваш_discord_public_key"
echo "   DISCORD_USE_INTERACTIONS=true"
echo "   API_KEY=ваш_arizona_api_key (опционально)"
echo ""
echo "4. 🎮 Discord Developer Portal:"
echo "   - Interactions Endpoint URL: https://ваше-приложение.onrender.com/discord/interactions"
echo ""
echo "🎉 Готово к развертыванию!"