import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from unified_config import BOT_TOKEN, CREATOR_ID, validate_config, logger, WELCOME_MESSAGE, HELP_MESSAGE_USER, HELP_MESSAGE_ADMIN, HELP_MESSAGE_CREATOR
from data_manager import DataManager
from filters import IsAdmin, IsCreator
from arizona_api import arizona_api
from discord_bot import discord_bot
from keep_alive import keep_alive

class UnifiedBot:
    def __init__(self):
        self.telegram_bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self.data_manager = DataManager()
        self.running = False
        self.restart_count = 0
        self.max_restarts = 100

    async def setup_telegram(self):
        self.setup_telegram_handlers()
        return True

    def setup_telegram_handlers(self):
        @self.dp.message(CommandStart())
        async def start_cmd(message):
            await message.answer(WELCOME_MESSAGE, parse_mode="HTML")

        @self.dp.message(Command("help"), IsCreator())
        async def help_creator(message):
            await message.answer(HELP_MESSAGE_CREATOR, parse_mode="HTML")

        @self.dp.message(Command("help"), IsAdmin())
        async def help_admin(message):
            await message.answer(HELP_MESSAGE_ADMIN, parse_mode="HTML")

        @self.dp.message(Command("help"))
        async def help_user(message):
            await message.answer(HELP_MESSAGE_USER, parse_mode="HTML")

        # Arizona RP servers
        @self.dp.message(Command("servers"))
        async def servers_command(message):
            loading_msg = await message.answer("🔄 Загружаю актуальный статус серверов...")
            try:
                servers_info = await arizona_api.get_servers_status_from_api()
            except Exception as e:
                logger.error(f"Error fetching servers: {e}")
                servers_info = await arizona_api.get_servers_info()
            await loading_msg.edit_text(servers_info)

        # Arizona RP stats
        @self.dp.message(Command("stats"))
        async def stats_command(message):
            args = message.text.split()
            if len(args) != 3:
                await message.answer("❌ Формат: /stats <ник> <ID сервера>")
                return
            nickname, server_id = args[1], int(args[2])
            is_valid_nick, nick_err = arizona_api.validate_nickname(nickname)
            if not is_valid_nick:
                await message.answer(nick_err)
                return
            is_valid_server, server_err = arizona_api.validate_server_id(server_id)
            if not is_valid_server:
                await message.answer(server_err)
                return
            processing_msg = await message.answer("⌛ Запрашиваю статистику...")
            data
