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

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from unified_config import (
    BOT_TOKEN, CREATOR_ID, validate_config, logger,
    WELCOME_MESSAGE, HELP_MESSAGE_USER, HELP_MESSAGE_ADMIN, HELP_MESSAGE_CREATOR,
    RANK_MESSAGE, SHOP_HELP_MESSAGE, COMMAND_DESCRIPTIONS
)
from data_manager import DataManager
from filters import IsAdmin, IsCreator
from arizona_api import arizona_api
from discord_bot import discord_bot
from keep_alive import keep_alive


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
            if not BOT_TOKEN:
                logger.error("BOT_TOKEN не задан")
                return False

            self.telegram_bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
            self.dp = Dispatcher(self.telegram_bot)
            self.data_manager = DataManager()

            # Setup filters and handlers
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
            await message.answer(WELCOME_MESSAGE)

        # Help command
        @self.dp.message(Command("help"), IsCreator())
        async def help_creator(message: Message):
            await message.answer(HELP_MESSAGE_CREATOR)

        @self.dp.message(Command("help"), IsAdmin())
        async def help_admin(message: Message):
            await message.answer(HELP_MESSAGE_ADMIN)

        @self.dp.message(Command("help"))
        async def help_user(message: Message):
            await message.answer(HELP_MESSAGE_USER)

        # Rules commands
        @self.dp.message(Command("rules"))
        async def rules_command(message: Message):
            rules = self.data_manager.get_rules()
            await message.answer(f"📋 <b>Правила чата:</b>\n\n{rules}")

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
            await message.answer(f"ℹ️ <b>Информация:</b>\n\n{info}")

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
            await message.answer(rank_info or RANK_MESSAGE)

        @self.dp.message(Command("setrank"), IsAdmin())
        async def set_rank_command(message: Message):
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.answer("❌ Использование: /setrank <информация о рангах>")
                return
            new_rank = message.text.split(" ", 1)[1]
            self.data_manager.set_rank(new_rank)
            await message.answer("✅ Информация о рангах успешно обновлена!")

        # Arizona RP stats
        @self.dp.message(Command("stats"))
        async def stats_command(message: Message):
            args = message.text.split() if message.text else []
            if len(args) != 3:
                await message.answer(
                    "❌ Неверный формат команды!\nИспользование: /stats <ник> <ID сервера>"
                )
                return
            nickname = args[1]
            try:
                server_id = int(args[2])
            except ValueError:
                await message.answer("❌ ID сервера должен быть числом")
                return

            # Validate nickname & server
            valid_nick, nick_err = arizona_api.validate_nickname(nickname)
            valid_server, server_err = arizona_api.validate_server_id(server_id)
            if not valid_nick:
                await message.answer(f"❌ {nick_err}")
                return
            if not valid_server:
                await message.answer(f"❌ {server_err}")
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
                logger.error(f"Telegram stats error: {e}")
                await processing_msg.edit_text("❌ Ошибка при получении статистики.")

        # Servers command
        @self.dp.message(Command("servers"))
        async def servers_command(message: Message):
            loading_msg = await message.answer("🔄 Загружаю статус серверов...")
            try:
                servers_info = await arizona_api.get_servers_status_from_api()
                refresh_kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton("🔄 Обновить", callback_data="refresh_servers")]
                ])
                await loading_msg.edit_text(servers_info, reply_markup=refresh_kb)
            except Exception as e:
                logger.error(f"Error fetching servers: {e}")
                fallback_info = arizona_api.get_servers_info()
                refresh_kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton("🔄 Обновить", callback_data="refresh_servers")]
                ])
                await loading_msg.edit_text(
                    f"⚠️ Не удалось получить актуальный статус серверов.\n{fallback_info}",
                    reply_markup=refresh_kb
                )

    async def set_bot_commands(self):
        """Set bot commands for BotFather menu"""
        if not self.telegram_bot:
            logger.error("Telegram bot не инициализирован")
            return
        commands = [BotCommand(command=c, description=d) for c, d in COMMAND_DESCRIPTIONS.items()]
        try:
            await self.telegram_bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")

    async def start_telegram(self):
        if not self.telegram_bot:
            logger.error("Telegram bot не инициализирован, пропускаем запуск")
            return
        logger.info("Starting Telegram bot...")
        await self.set_bot_commands()
        await self.dp.start_polling(self.telegram_bot, skip_updates=True)

    async def start_discord(self):
        if discord_bot.setup():
            await discord_bot.start()
        else:
            logger.info("Discord bot not configured, running Telegram only")

    async def run(self):
        if not validate_config():
            logger.error("Config validation failed")
            return False

        self.restart_count += 1
        if not await self.setup_telegram():
            return False

        self.running = True
        keep_alive()

        telegram_task = asyncio.create_task(self.start_telegram())
        discord_task = asyncio.create_task(self.start_discord())

        await asyncio.gather(telegram_task, discord_task, return_exceptions=True)

    async def cleanup(self):
        self.running = False
        if self.telegram_bot:
            await self.telegram_bot.session.close()
        await discord_bot.close()


async def main():
    if not validate_config():
        sys.exit(1)

    bot = UnifiedBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
