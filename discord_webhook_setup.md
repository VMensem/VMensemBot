# Discord Interactions Endpoint URL Setup

Теперь MensemBot поддерживает Discord Interactions через HTTP webhook вместо WebSocket подключения.

## Настройка Discord Application

1. **Создайте Discord Application:**
   - Перейдите на https://discord.com/developers/applications
   - Нажмите "New Application"
   - Введите имя "MensemBot" 
   - Сохраните Application ID

2. **Настройка Interactions Endpoint URL:**
   - В разделе "General Information" найдите "Interactions Endpoint URL"
   - Введите: `https://ваш-домен.replit.app/discord/interactions`
   - Сохраните изменения

3. **Получите необходимые токены:**
   - **Application ID** - из General Information
   - **Public Key** - из General Information  
   - **Bot Token** - из раздела Bot (если нужен для дополнительных функций)

## Переменные окружения

Добавьте в Replit Secrets:

```
DISCORD_APPLICATION_ID=ваш_application_id
DISCORD_PUBLIC_KEY=ваш_public_key
DISCORD_USE_INTERACTIONS=true
```

Опционально (для расширенных функций):
```
DISCORD_TOKEN=ваш_bot_token
```

## Преимущества Interactions Endpoint URL

✅ **Не требует постоянного WebSocket подключения**
✅ **Меньше потребление ресурсов**
✅ **Автоматическая регистрация slash команд**
✅ **Поддержка Discord embed сообщений**
✅ **Работает с бесплатными хостингами**

## Доступные команды Discord

- `/help` - Список команд
- `/rules` - Правила сервера
- `/info` - Информация
- `/rank` - Информация о рангах  
- `/servers` - Серверы Arizona RP
- `/stats <ник> <сервер>` - Статистика игрока Arizona RP

## Тестирование

1. Пригласите бота на Discord сервер с правами "Use Slash Commands"
2. Используйте команду `/help` для проверки
3. Проверьте endpoint: `https://ваш-домен.replit.app/health`

## Примечание

Если вы предпочитаете использовать Interactions вместо традиционного bot подключения, установите:
```
DISCORD_USE_INTERACTIONS=true
```

При этом старый Discord bot (через WebSocket) отключится, и будет работать только webhook endpoint.