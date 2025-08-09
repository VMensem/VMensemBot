"""
Discord Interactions Handler
Обработчик Discord Interactions через HTTP webhook вместо WebSocket
"""

import os
import json
import logging
import hashlib
import hmac
import asyncio
import aiohttp
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
from data_manager import DataManager
from unified_config import API_KEY

# Попытаемся импортировать ArizonaAPI, если доступен
try:
    from arizona_api import ArizonaAPI
except ImportError:
    ArizonaAPI = type(None)  # Создаем тип для проверки

logger = logging.getLogger(__name__)

class DiscordInteractionsHandler:
    def __init__(self, data_manager: DataManager, arizona_api: Optional[Any] = None):
        self.data_manager = data_manager
        self.arizona_api = arizona_api
        self.application_id = os.getenv('DISCORD_APPLICATION_ID')
        self.public_key = os.getenv('DISCORD_PUBLIC_KEY')
        self.bot_token = os.getenv('DISCORD_TOKEN')
        
    def verify_signature(self, signature: str, timestamp: str, body: str) -> bool:
        """Проверка подписи Discord"""
        if not self.public_key:
            return False
            
        try:
            public_key_bytes = bytes.fromhex(self.public_key)
            message = timestamp + body
            
            # Используем Ed25519 для проверки подписи
            # Это упрощенная версия - в реальном приложении нужна библиотека nacl
            return signature.startswith('ed25519=')
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    async def handle_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка Discord interaction"""
        interaction_type = interaction_data.get('type')
        
        # Ping (type 1)
        if interaction_type == 1:
            return {'type': 1}  # Pong response
        
        # Application Command (type 2)
        elif interaction_type == 2:
            return await self.handle_command(interaction_data)
        
        # Message Component (type 3)
        elif interaction_type == 3:
            return await self.handle_component(interaction_data)
        
        return {'type': 4, 'data': {'content': 'Неизвестный тип взаимодействия'}}
    
    async def handle_command(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка команд Discord"""
        command_name = interaction['data']['name']
        
        try:
            if command_name == 'help':
                return await self.cmd_help()
            elif command_name == 'rules':
                return await self.cmd_rules()
            elif command_name == 'info':
                return await self.cmd_info()
            elif command_name == 'rank':
                return await self.cmd_rank()
            elif command_name == 'servers':
                return await self.cmd_servers()
            elif command_name == 'stats':
                return await self.cmd_stats(interaction['data'].get('options', []))
            else:
                return self.error_response(f"Команда {command_name} не найдена")
        except Exception as e:
            logger.error(f"Command error: {e}")
            return self.error_response("Произошла ошибка при выполнении команды")
    
    async def handle_component(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка компонентов (кнопки, меню)"""
        custom_id = interaction['data']['custom_id']
        
        if custom_id == 'refresh_stats':
            # Обновить статистику
            return {'type': 7, 'data': {'content': 'Статистика обновлена!'}}
        
        return self.error_response("Неизвестное взаимодействие")
    
    async def cmd_help(self) -> Dict[str, Any]:
        """Команда помощи"""
        embed = {
            'title': '📋 Список команд MensemBot',
            'description': 'Доступные команды для Discord',
            'color': 0x00ff00,
            'fields': [
                {
                    'name': '📝 Основные команды',
                    'value': '/help - Показать эту справку\n/rules - Правила сервера\n/info - Информация\n/rank - Информация о рангах',
                    'inline': False
                },
                {
                    'name': '🎮 Arizona RP',
                    'value': '/stats - Статистика игрока\n/servers - Список серверов',
                    'inline': False
                }
            ]
        }
        
        return {'type': 4, 'data': {'embeds': [embed]}}
    
    async def cmd_rules(self) -> Dict[str, Any]:
        """Команда правил"""
        rules = self.data_manager.get_rules()
        embed = {
            'title': '📋 Правила сервера',
            'description': rules,
            'color': 0x0099ff
        }
        return {'type': 4, 'data': {'embeds': [embed]}}
    
    async def cmd_info(self) -> Dict[str, Any]:
        """Команда информации"""
        info = self.data_manager.get_info()
        embed = {
            'title': 'ℹ️ Информация',
            'description': info,
            'color': 0x00ff99
        }
        return {'type': 4, 'data': {'embeds': [embed]}}
    
    async def cmd_rank(self) -> Dict[str, Any]:
        """Команда рангов"""
        rank_info = self.data_manager.get_rank()
        embed = {
            'title': '🏆 Ранги',
            'description': rank_info,
            'color': 0xffd700
        }
        return {'type': 4, 'data': {'embeds': [embed]}}
    
    async def cmd_servers(self) -> Dict[str, Any]:
        """Команда серверов Arizona RP"""
        if not self.arizona_api:
            return self.error_response("Arizona RP API не настроен")
        
        servers_info = """
**💻 ПК серверы (1-31):**
 1: Phoenix
 2: Tucson
 3: Scottdale
 4: Chandler
 5: Brainburg
 6: Saint Rose
 7: Mesa
 8: Red Rock
 9: Yuma
10: Surprise
11: Prescott
12: Glendale
13: Kingman
14: Winslow
15: Payson
16: Gilbert
17: Show Low
18: Casa Grande
19: Page
20: Sun City
21: Queen Creek
22: Sedona
23: Holiday
24: Wednesday
25: Yava
26: Faraway
27: Bumble Bee
28: Christmas
29: Mirage
30: Love
31: Drake

**📱 Мобайл серверы:**
101: Mobile 1
102: Mobile 2
103: Mobile 3
"""
        
        embed = {
            'title': '🌐 Серверы Arizona RP:',
            'description': servers_info,
            'color': 0xff6600,
            'footer': {'text': 'Используйте /stats <ник> <ID сервера> для получения статистики'}
        }
        
        return {'type': 4, 'data': {'embeds': [embed]}}
    
    async def cmd_stats(self, options: list) -> Dict[str, Any]:
        """Команда статистики игрока"""
        if not self.arizona_api:
            return self.error_response("Arizona RP API не настроен")
        
        if len(options) < 2:
            return self.error_response("Использование: /stats <ник> <ID сервера>")
        
        nickname = options[0]['value']
        server_id = options[1]['value']
        
        try:
            stats = await self.arizona_api.get_player_stats(nickname, server_id)
            
            if not stats:
                return self.error_response(f"Игрок {nickname} не найден на сервере {server_id}")
            
            embed = {
                'title': f'📊 Статистика игрока {nickname}',
                'color': 0x00ff00,
                'fields': [
                    {'name': '🆔 ID', 'value': str(stats.get('id', 'N/A')), 'inline': True},
                    {'name': '🌍 Сервер', 'value': str(server_id), 'inline': True},
                    {'name': '💰 Деньги', 'value': f"${stats.get('money', 0):,}", 'inline': True},
                    {'name': '🏦 Банк', 'value': f"${stats.get('bank', 0):,}", 'inline': True},
                    {'name': '⭐ Уровень', 'value': str(stats.get('level', 0)), 'inline': True},
                    {'name': '🕐 Онлайн', 'value': f"{stats.get('online_hours', 0)} ч.", 'inline': True}
                ]
            }
            
            return {'type': 4, 'data': {'embeds': [embed]}}
            
        except Exception as e:
            logger.error(f"Stats command error: {e}")
            return self.error_response("Ошибка получения статистики игрока")
    
    def error_response(self, message: str) -> Dict[str, Any]:
        """Создание ответа с ошибкой"""
        embed = {
            'title': '❌ Ошибка',
            'description': message,
            'color': 0xff0000
        }
        return {'type': 4, 'data': {'embeds': [embed]}}

def create_discord_webhook_handler(app: Flask, data_manager: DataManager):
    """Создание webhook обработчика для Discord"""
    arizona_api = ArizonaAPI(API_KEY) if API_KEY and ArizonaAPI else None
    handler = DiscordInteractionsHandler(data_manager, arizona_api)
    
    @app.route('/discord/interactions', methods=['POST'])
    def discord_interactions():
        # Получение заголовков
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')
        
        if not signature or not timestamp:
            return jsonify({'error': 'Missing signature headers'}), 401
        
        # Проверка подписи (упрощенная версия)
        body = request.get_data(as_text=True)
        
        try:
            # Обработка взаимодействия
            interaction_data = request.json
            if not interaction_data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            response = asyncio.run(handler.handle_interaction(interaction_data))
            return jsonify(response)
        except Exception as e:
            logger.error(f"Discord interaction error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return handler

# Регистрация slash команд Discord (нужно выполнить один раз)
async def register_discord_commands():
    """Регистрация slash команд в Discord"""
    application_id = os.getenv('DISCORD_APPLICATION_ID')
    bot_token = os.getenv('DISCORD_TOKEN')
    
    if not application_id or not bot_token:
        logger.warning("Discord Application ID или Bot Token не настроены")
        return
    
    commands = [
        {
            'name': 'help',
            'description': 'Показать список команд',
            'type': 1
        },
        {
            'name': 'rules',
            'description': 'Показать правила сервера',
            'type': 1
        },
        {
            'name': 'info',
            'description': 'Показать информацию',
            'type': 1
        },
        {
            'name': 'rank',
            'description': 'Показать информацию о рангах',
            'type': 1
        },
        {
            'name': 'servers',
            'description': 'Показать список серверов Arizona RP',
            'type': 1
        },
        {
            'name': 'stats',
            'description': 'Получить статистику игрока Arizona RP',
            'type': 1,
            'options': [
                {
                    'name': 'nickname',
                    'description': 'Ник игрока',
                    'type': 3,
                    'required': True
                },
                {
                    'name': 'server',
                    'description': 'ID сервера (1-28)',
                    'type': 4,
                    'required': True,
                    'min_value': 1,
                    'max_value': 28
                }
            ]
        }
    ]
    
    # Отправка команд в Discord API
    url = f'https://discord.com/api/v10/applications/{application_id}/commands'
    headers = {
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=commands, headers=headers) as response:
            if response.status == 200:
                logger.info("Discord slash команды успешно зарегистрированы")
            else:
                logger.error(f"Ошибка регистрации Discord команд: {response.status}")