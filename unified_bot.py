#!/usr/bin/env python3
"""
Unified MensemBot - Multi-platform bot for Telegram and Discord
Supports community management and Arizona RP statistics
"""

import asyncio
import logging
import signal
import sys
from typing import Optional
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from unified_config import (
    BOT_TOKEN, CREATOR_ID, validate_config, logger,
    WELCOME_MESSAGE, HELP_MESSAGE_USER, HELP_MESSAGE_ADMIN, HELP_MESSAGE_CREATOR,RANK_MESSAGE, SHOP_HELP_MESSAGE,
    COMMAND_DESCRIPTIONS
)
from data_manager import DataManager
from filters import IsAdmin, IsCreator
from arizona_api import arizona_api
from discord_bot import discord_bot
from keep_alive import keep_alive

# Если токен в environment (Render)
if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not CREATOR_ID:
    CREATOR_ID = int(os.environ.get("CREATOR_ID", 0))

class UnifiedBot:
    """Main unified bot class supporting both Telegram and Discord"""
    
    def __init__(self):
        self.telegram_bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.data_manager: Optional[DataManager] = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 100
        
    async def setup_telegram(self):
        """Setup Telegram bot"""
        try:
            self.telegram_bot = Bot(token=BOT_TOKEN)
            self.dp = Dispatcher()
            self.data_manager = DataManager()
            
            # Setup filters
            self.dp.message.filter(lambda message: message.chat.type in ['private', 'group', 'supergroup'])
            
            # Setup handlers
            self.setup_telegram_handlers()
            
            logger.info("Telegram bot configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Telegram bot: {e}")
            return False
    
    def setup_telegram_handlers(self):
        """Setup Telegram bot handlers"""
        
        # Start command
        @self.dp.message(CommandStart())
        async def start_command(message: Message):
            await message.answer(WELCOME_MESSAGE, parse_mode="HTML")
        
        # Help command
        #Создателю
        @self.dp.message(Command("help"), IsCreator())
        async def help_command(message: Message):
            await message.answer(HELP_MESSAGE_CREATOR, parse_mode="HTML")

        #Админы
        @self.dp.message(Command("help"), IsAdmin())
        async def help_command(message: Message):
            await message.answer(HELP_MESSAGE_ADMIN, parse_mode="HTML")

        #Игроки
        @self.dp.message(Command("help"))
        async def help_command(message: Message):
            await message.answer(HELP_MESSAGE_USER, parse_mode="HTML")
        
        # Rules commands
        @self.dp.message(Command("rules"))
        async def rules_command(message: Message):
            rules = self.data_manager.get_rules()
            await message.answer(f"📋 <b>Правила чата:</b>\n\n{rules}", parse_mode="HTML")
        
        @self.dp.message(Command("setrules"), IsAdmin())
        async def set_rules_command(message: Message):
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.answer("❌ Использование: /setrules <новые правила>")
                return
            
            new_rules = message.text.split(" ", 1)[1]
            self.data_manager.set_rules(new_rules)
            await message.answer("✅ Правила успешно обновлены!")
        
        # Info commands
        @self.dp.message(Command("info"))
        async def info_command(message: Message):
            info = self.data_manager.get_info()
            await message.answer(f"ℹ️ <b>Информация:</b>\n\n{info}", parse_mode="HTML")
        
        @self.dp.message(Command("setinfo"), IsAdmin())
        async def set_info_command(message: Message):
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.answer("❌ Использование: /setinfo <новая информация>")
                return
            
            new_info = message.text.split(" ", 1)[1]
            self.data_manager.set_info(new_info)
            await message.answer("✅ Информация успешно обновлена!")

        # Rank commands
        @self.dp.message(Command("rank"))
        async def rank_command(message: Message):
            rank_info = self.data_manager.get_rank()
            if rank_info:
                await message.answer(f"🏆 <b>Ранги:</b>\n\n{rank_info}", parse_mode="HTML")
            else:
                await message.answer(RANK_MESSAGE, parse_mode="HTML")
        
        @self.dp.message(Command("setrank"), IsAdmin())
        async def set_rank_command(message: Message):
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.answer("❌ Использование: /setrank <информация о рангах>")
                return
            
            new_rank = message.text.split(" ", 1)[1]
            self.data_manager.set_rank(new_rank)
            await message.answer("✅ Информация о рангах успешно обновлена!")

        # ID command
        @self.dp.message(Command("id"))
        async def id_command(message: Message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            response = f"🆔 <b>Ваша информация:</b>\n\n"
            response += f"👤 User ID: <code>{user_id}</code>\n"
            response += f"💬 Chat ID: <code>{chat_id}</code>\n"
            
            if message.chat.type != 'private':
                response += f"📱 Chat Type: {message.chat.type}"
            
            await message.answer(response, parse_mode="HTML")

        # Shop command
        @self.dp.message(Command("shop"))
        async def shop_command(message: Message):
            if message.chat.type != 'private':
                await message.answer("🔒 Команда /shop работает только в личных сообщениях с ботом.")
                return
            
            await message.answer(SHOP_HELP_MESSAGE, parse_mode="HTML")
        
        # Idea command
        @self.dp.message(Command("idea"))
        async def idea_command(message: Message):
            args = message.text.split(maxsplit=1) if message.text else []
            
            if len(args) < 2:
                await message.answer(
                    "💡 <b>Команда /idea</b>\n\n"
                    "Отправьте свою идею руководству семьи!\n\n"
                    "<b>Использование:</b> /idea Ваша идея",
                    parse_mode="HTML"
                )
                return
            
            idea_text = args[1].strip()
            if len(idea_text) < 10:
                await message.answer("❌ Идея слишком короткая. Опишите её подробнее (минимум 10 символов).")
                return
            
            user = message.from_user
            user_info = f"@{user.username}" if user.username else user.first_name
            idea_message = f"💡 <b>НОВАЯ ИДЕЯ ОТ ИГРОКА</b>\n\n👤 {user_info} (ID: {user.id})\n📝 {idea_text}\n⏰ {message.date.strftime('%d.%m.%Y %H:%M')}"
            
            family_chat_id = self.data_manager.get_family_chat_id()
            if family_chat_id:
                await self.telegram_bot.send_message(family_chat_id, idea_message, parse_mode="HTML")
            await self.telegram_bot.send_message(CREATOR_ID, "💡 Новая идея в чате руководства!")
            await message.answer("✅ Ваша идея успешно отправлена руководству семьи!", parse_mode="HTML")

        # Stats and servers commands
        @self.dp.message(Command("stats"))
        async def stats_command(message: Message):
            args = message.text.split() if message.text else []
            if len(args) != 3:
                await message.answer("❌ Неверный формат команды! Использование: /stats <ник> <ID сервера>")
                return
            
            nickname = args[1]
            try:
                server_id = int(args[2])
            except ValueError:
                await message.answer("❌ ID сервера должен быть числом.")
                return
            
            # Validate nickname and server
            is_valid_nick, nick_error = arizona_api.validate_nickname(nickname)
            if not is_valid_nick:
                await message.answer(f"❌ {nick_error}")
                return
            is_valid_server, server_error = arizona_api.validate_server_id(server_id)
            if not is_valid_server:
                await message.answer(f"❌ {server_error}")
                return
            
            processing_msg = await message.answer("⌛ Запрашиваю статистику...")
            try:
                data, error = await arizona_api.fetch_player_stats(nickname, server_id)
                if error:
                    await processing_msg.edit_text(error)
                    return
                formatted_stats = arizona_api.format_stats(data, nickname, server_id) if data else "❌ Не удалось получить данные"
                if len(formatted_stats) > 4096:
                    formatted_stats = formatted_stats[:4093] + "..."
                await processing_msg.edit_text(formatted_stats)
            except Exception as e:
                logger.error(f"Error in stats command: {e}")
                await processing_msg.edit_text("❌ Произошла ошибка при получении статистики.")
        
        @self.dp.message(Command("servers"))
        async def servers_command(message: Message):
            loading_msg = await message.answer("🔄 Загружаю актуальный статус серверов...")
            try:
                servers_info = await arizona_api.get_servers_status_from_api()
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_servers")]])
                await loading_msg.edit_text(servers_info, reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Error fetching servers: {e}")
                fallback_info = arizona_api.get_servers_info()
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_servers")]])
                await loading_msg.edit_text(f"⚠️ Не удалось получить актуальный статус серверов.\n{fallback_info}", reply_markup=keyboard)

    async def set_bot_commands(self):
        commands = [BotCommand(command=c, description=d) for c,d in COMMAND_DESCRIPTIONS.items()]
        try:
            await self.telegram_bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")

    async def start_telegram(self):
        try:
            logger.info("Starting Telegram bot...")
            await self.set_bot_commands()
            await self.dp.start_polling(self.telegram_bot, skip_updates=True)
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
            raise

    async def start_discord(self):
        if discord_bot.setup():
            try:
                await discord_bot.start()
            except Exception as e:
                logger.error(f"Discord bot failed to start: {e}")
        else:
            logger.info("Discord bot not configured, running Telegram only")

    async def run(self):
        if not validate_config():
            logger.error("Configuration validation failed")
            return False
        self.restart_count += 1
        self.running = True
        telegram_task = asyncio.create_task(self.start_telegram(), name="telegram_bot")
        discord_task = asyncio.create_task(self.start_discord(), name="discord_bot")
        keep_alive()
        await asyncio.gather(telegram_task, discord_task, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(UnifiedBot().run())
