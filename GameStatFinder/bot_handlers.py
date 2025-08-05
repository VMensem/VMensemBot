import logging
from typing import Union

import discord
from discord.ext import commands
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from api_client import api_client
from utils import validate_nickname, validate_server_id, truncate_message, escape_markdown

logger = logging.getLogger(__name__)

class DiscordBotHandlers:
    """Discord bot command handlers"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.setup_events()
        self.setup_commands()
    
    def setup_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f"Discord бот запущен как {self.bot.user}")
            print(f"🤖 Discord бот запущен как {self.bot.user}")
            
            # Set bot status
            activity = discord.Game(name="!stats <ник> <сервер>")
            await self.bot.change_presence(activity=activity)
        
        @self.bot.event
        async def on_command_error(ctx: commands.Context, error: Exception):
            """Handle command errors"""
            logger.error(f"Discord command error: {error}")
            
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("❌ Команда не найдена. Используйте `!stats <ник> <ID сервера>`")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("❌ Неверный формат команды. Используйте: `!stats <ник> <ID сервера>`")
            elif isinstance(error, commands.BadArgument):
                await ctx.send("❌ Неверные аргументы. ID сервера должен быть числом.")
            else:
                await ctx.send("❌ Произошла ошибка при выполнении команды.")
    
    def setup_commands(self):
        """Setup Discord bot commands"""
        
        @self.bot.command(name="stats", help="Получить статистику игрока")
        async def discord_stats(ctx: commands.Context, nickname: str = "", server_id: int = 0):
            """Discord stats command handler"""
            
            # Show typing indicator
            async with ctx.typing():
                # Validate arguments
                if not nickname or server_id == 0:
                    await ctx.send("❌ Неверный формат команды!\n**Использование:** `!stats <ник> <ID сервера>`\n\n**Доступные серверы:** ПК 1-31, Мобайл 101-103\n**Посмотреть все серверы:** `!servers`")
                    return
                
                # Validate nickname
                is_valid_nick, nick_error = validate_nickname(nickname)
                if not is_valid_nick:
                    await ctx.send(f"❌ {nick_error}")
                    return
                
                # Validate server ID
                is_valid_server, server_error = validate_server_id(server_id)
                if not is_valid_server:
                    await ctx.send(f"❌ {server_error}")
                    return
                
                # Fetch statistics
                data, error = await api_client.fetch_player_stats(nickname, server_id)
                
                if error:
                    await ctx.send(error)
                    return
                
                # Format and send response
                if data is not None:
                    formatted_stats = api_client.format_stats(data, nickname, server_id)
                else:
                    formatted_stats = "❌ Не удалось получить данные"
                
                # Truncate message if too long for Discord
                formatted_stats = truncate_message(formatted_stats, 2000)
                
                await ctx.send(formatted_stats)
        
        @self.bot.command(name="servers", help="Показать все серверы Arizona RP")
        async def discord_servers(ctx: commands.Context):
            """Discord servers command"""
            server_msg = "🌐 **Серверы Arizona RP:**\n\n"
            
            # ПК серверы
            server_msg += "💻 **ПК серверы (1-31):**\n"
            pc_servers = ", ".join([str(i) for i in range(1, 32)])
            server_msg += f"{pc_servers}\n\n"
            
            # Мобайл серверы
            server_msg += "📱 **Мобайл серверы:**\n"
            server_msg += "101, 102, 103\n"
            
            server_msg += "\n**Использование:** `!stats <ник> <ID сервера>`"
            server_msg += "\n**Пример:** `!stats PlayerName 1`"
            
            await ctx.send(server_msg)

        @self.bot.command(name="help", help="Показать справку по командам")
        async def discord_help(ctx: commands.Context):
            """Discord help command"""
            help_text = """
🤖 **Справка по командам бота Arizona RP**

**!stats <ник> <ID сервера>** - Получить информацию об игроке
**!servers** - Показать все серверы Arizona RP

**Доступные серверы Arizona RP:** ПК 1-31, Мобайл 101-103

**Пример:** `!stats PlayerName 1`
            """
            await ctx.send(help_text)

class TelegramBotHandlers:
    """Telegram bot command handlers"""
    
    def __init__(self):
        self.dp = Dispatcher()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup Telegram bot handlers"""
        
        @self.dp.message(Command("start"))
        async def tg_start(message: Message):
            """Telegram start command handler"""
            welcome_text = """
🤖 **Добро пожаловать в бота статистики Arizona RP!**

**Доступные команды:**
• `/stats <ник> <ID сервера>` - Получить статистику игрока
• `/servers` - Показать все серверы Arizona RP

**Доступные серверы Arizona RP:** ПК 1-31, Мобайл 101-103

**Пример:** `/stats PlayerName 1`

Для получения справки используйте /help
            """
            await message.answer(welcome_text, parse_mode="Markdown")
        
        @self.dp.message(Command("servers"))
        async def tg_servers(message: Message):
            """Telegram servers command handler"""
            server_msg = "🌐 **Серверы Arizona RP:**\n\n"
            
            # ПК серверы
            server_msg += "💻 **ПК серверы (1-31):**\n"
            pc_servers = ", ".join([str(i) for i in range(1, 32)])
            server_msg += f"{pc_servers}\n\n"
            
            # Мобайл серверы
            server_msg += "📱 **Мобайл серверы:**\n"
            server_msg += "101, 102, 103\n"
            
            server_msg += "\n**Использование:** `/stats <ник> <ID сервера>`"
            server_msg += "\n**Пример:** `/stats PlayerName 1`"
            
            await message.answer(server_msg, parse_mode="Markdown")
        
        @self.dp.message(Command("help"))
        async def tg_help(message: Message):
            """Telegram help command handler"""
            help_text = """
🤖 **Справка по командам бота Arizona RP**

**/stats <ник> <ID сервера>** - Получить информацию об игроке
**/servers** - Показать все серверы Arizona RP
**/help** - Показать эту справку
**/start** - Начать работу с ботом

**Доступные серверы Arizona RP:** ПК 1-31, Мобайл 101-103

**Пример использования:**
`/stats PlayerName 1`

**Ограничения:**
• Ник должен содержать 3-24 символа
• Только буквы, цифры и подчёркивания
            """
            await message.answer(help_text, parse_mode="Markdown")
        
        @self.dp.message(Command("stats"))
        async def tg_stats(message: Message):
            """Telegram stats command handler"""
            
            # Parse command arguments
            args = message.text.split() if message.text else []
            
            if len(args) != 3:
                await message.answer(
                    "❌ Неверный формат команды!\n\n"
                    "**Использование:** `/stats <ник> <ID сервера>`\n\n"
                    "**Доступные серверы:** ПК 1-31, Мобайл 101-103\n"
                    "**Посмотреть все серверы:** `/servers`\n\n"
                    "**Пример:** `/stats PlayerName 1`",
                    parse_mode="Markdown"
                )
                return
            
            nickname = args[1]
            
            # Validate server ID
            try:
                server_id = int(args[2])
            except ValueError:
                await message.answer("❌ ID сервера должен быть числом.")
                return
            
            # Validate nickname
            is_valid_nick, nick_error = validate_nickname(nickname)
            if not is_valid_nick:
                await message.answer(f"❌ {nick_error}")
                return
            
            # Validate server ID
            is_valid_server, server_error = validate_server_id(server_id)
            if not is_valid_server:
                await message.answer(f"❌ {server_error}")
                return
            
            # Send "processing" message
            processing_msg = await message.answer("⌛ Запрашиваю статистику...")
            
            try:
                # Fetch statistics
                data, error = await api_client.fetch_player_stats(nickname, server_id)
                
                if error:
                    await processing_msg.edit_text(error)
                    return
                
                # Format response
                if data is not None:
                    formatted_stats = api_client.format_stats(data, nickname, server_id)
                else:
                    formatted_stats = "❌ Не удалось получить данные"
                
                # Truncate message if too long for Telegram
                formatted_stats = truncate_message(formatted_stats, 4096)
                
                # Remove problematic markdown characters and try without parse_mode first
                safe_stats = formatted_stats.replace('├─', '  ').replace('└─', '  ').replace('*', '').replace('_', '')
                try:
                    await processing_msg.edit_text(safe_stats)
                except Exception as e:
                    logger.error(f"Failed to send formatted message: {e}")
                    # Fallback to simple text
                    simple_msg = f"👤 Информация об игроке {nickname}\n\nИгрок найден на сервере {server_id}"
                    await processing_msg.edit_text(simple_msg)
                
            except Exception as e:
                logger.error(f"Error in Telegram stats command: {e}")
                await processing_msg.edit_text("❌ Произошла ошибка при получении статистики.")
