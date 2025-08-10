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
    WELCOME_MESSAGE, HELP_MESSAGE, RANK_MESSAGE, SHOP_HELP_MESSAGE,
    COMMAND_DESCRIPTIONS
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
        @self.dp.message(Command("help"))
        async def help_command(message: Message):
            await message.answer(HELP_MESSAGE, parse_mode="HTML")
        
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
            
            await message.answer(SHOP_HELP_MESSAGE)

        # Shop application handler (media with caption)
        @self.dp.message(F.photo | F.video, F.chat.type == 'private')
        async def shop_application_handler(message: Message):
            if not message.caption:
                return  # Ignore media without caption
                
            caption = message.caption.strip()
            
            # Check if it's a shop application (contains required fields)
            if any(keyword in caption.lower() for keyword in ['ник:', 'ранг:', 'доказательства:']):
                user = message.from_user
                user_info = f"👤 @{user.username}" if user.username else f"👤 {user.first_name}"
                
                application_text = f"""
⭐ <b>НОВАЯ ЗАЯВКА НА РАНГ</b>

{user_info} (ID: {user.id})

📝 <b>Заявка:</b>
{caption}

⏰ Время подачи: {message.date.strftime('%d.%m.%Y %H:%M')}
"""
                
                try:
                    # Create inline keyboard for family leadership
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Выдано",
                                callback_data=f"rank_approve_{user.id}"
                            ),
                            InlineKeyboardButton(
                                text="❌ Отказано", 
                                callback_data=f"rank_reject_{user.id}"
                            )
                        ]
                    ])
                    
                    # Send to family leadership chat
                    family_chat_id = self.data_manager.get_family_chat_id()
                    if family_chat_id:
                        if message.photo:
                            await self.telegram_bot.send_photo(
                                family_chat_id,
                                message.photo[-1].file_id,
                                caption=application_text,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                        elif message.video:
                            await self.telegram_bot.send_video(
                                family_chat_id,
                                message.video.file_id,
                                caption=application_text,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                    
                    # Send notification to creator (without media)
                    await self.telegram_bot.send_message(
                        CREATOR_ID,
                        "⭐ Новая заявка в чате руководства!"
                    )
                    
                    await message.answer(
                        "✅ Ваша заявка на ранг успешно отправлена!\n"
                        "📨 Руководство семьи рассмотрит заявку в ближайшее время."
                    )
                    
                    logger.info(f"Rank application sent from {user.id} to family leadership")
                    
                except Exception as e:
                    logger.error(f"Failed to send rank application: {e}")
                    await message.answer(
                        "❌ Произошла ошибка при отправке заявки.\n"
                        "Попробуйте позже или обратитесь к администратору."
                    )

        # Idea command  
        @self.dp.message(Command("idea"))
        async def idea_command(message: Message):
            args = message.text.split(maxsplit=1) if message.text else []
            
            if len(args) < 2:
                await message.answer(
                    "💡 <b>Команда /idea</b>\n\n"
                    "Отправьте свою идею руководству семьи!\n\n"
                    "<b>Использование:</b> /idea Ваша идея\n\n"
                    "<b>Пример:</b> /idea Предлагаю добавить еженедельные турниры",
                    parse_mode="HTML"
                )
                return
                
            idea_text = args[1].strip()
            
            if len(idea_text) < 10:
                await message.answer("❌ Идея слишком короткая. Опишите её подробнее (минимум 10 символов).")
                return
                
            user = message.from_user
            user_info = f"@{user.username}" if user.username else user.first_name
            
            idea_message = f"""
💡 <b>НОВАЯ ИДЕЯ ОТ ИГРОКА</b>

👤 <b>От:</b> {user_info} (ID: {user.id})
💬 <b>Чат:</b> {message.chat.title or 'Личные сообщения'}

📝 <b>Идея:</b>
{idea_text}

⏰ <b>Время:</b> {message.date.strftime('%d.%m.%Y %H:%M')}
"""
            
            try:
                # Send to family leadership chat
                family_chat_id = self.data_manager.get_family_chat_id()
                if family_chat_id:
                    await self.telegram_bot.send_message(
                        family_chat_id,
                        idea_message,
                        parse_mode="HTML"
                    )
                
                # Send notification to creator (without full text)
                await self.telegram_bot.send_message(
                    CREATOR_ID,
                    "💡 Новая идея в чате руководства!"
                )
                
                await message.answer(
                    "✅ Ваша идея успешно отправлена руководству семьи!\n"
                    "📨 Спасибо за то что вы с нами <3."
                )
                
                logger.info(f"Idea sent from {user.id}: {idea_text[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to send idea: {e}")
                await message.answer(
                    "❌ Произошла ошибка при отправке идеи.\n"
                    "Попробуйте позже или обратитесь к администратору."
                )
        
        # Arizona RP Stats command
        @self.dp.message(Command("stats"))
        async def stats_command(message: Message):
            args = message.text.split() if message.text else []
            
            if len(args) != 3:
                await message.answer(
                    "❌ Неверный формат команды!\n\n"
                    "<b>Использование:</b> /stats &lt;ник&gt; &lt;ID сервера&gt;\n\n"
                    "<b>Доступные серверы:</b> ПК 1-31, Мобайл 101-103\n"
                    "<b>Посмотреть все серверы:</b> /servers\n\n"
                    "<b>Пример:</b> /stats PlayerName 1",
                    parse_mode="HTML"
                )
                return
            
            nickname = args[1]
            
            try:
                server_id = int(args[2])
            except ValueError:
                await message.answer("❌ ID сервера должен быть числом.")
                return
            
            # Validate nickname
            is_valid_nick, nick_error = arizona_api.validate_nickname(nickname)
            if not is_valid_nick:
                await message.answer(f"❌ {nick_error}")
                return
            
            # Validate server ID
            is_valid_server, server_error = arizona_api.validate_server_id(server_id)
            if not is_valid_server:
                await message.answer(f"❌ {server_error}")
                return
            
            # Send processing message
            processing_msg = await message.answer("⌛ Запрашиваю статистику...")
            
            try:
                # Fetch statistics
                data, error = await arizona_api.fetch_player_stats(nickname, server_id)
                
                if error:
                    await processing_msg.edit_text(error)
                    return
                
                # Format response
                if data is not None:
                    formatted_stats = arizona_api.format_stats(data, nickname, server_id)
                else:
                    formatted_stats = "❌ Не удалось получить данные"
                
                # Truncate message if too long for Telegram
                if len(formatted_stats) > 4096:
                    formatted_stats = formatted_stats[:4093] + "..."
                
                # Send without parse_mode to avoid markdown issues
                await processing_msg.edit_text(formatted_stats)
                
            except Exception as e:
                logger.error(f"Error in Telegram stats command: {e}")
                await processing_msg.edit_text("❌ Произошла ошибка при получении статистики.")
        
        # Servers command
        @self.dp.message(Command("servers"))
        async def servers_command(message: Message):
            # Отправляем сообщение о загрузке
            loading_msg = await message.answer("🔄 Загружаю актуальный статус серверов Arizona RP...")
            
            try:
                # Получаем актуальную информацию о серверах
                servers_info = await arizona_api.get_servers_status_from_api()
                
                # Создаем inline кнопку для обновления
                refresh_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_servers")]
                ])
                
                await loading_msg.edit_text(
                    servers_info, 
                    parse_mode="Markdown",
                    reply_markup=refresh_keyboard
                )
                
            except Exception as e:
                logger.error(f"Error in servers command: {e}")
                # В случае ошибки показываем базовую информацию
                fallback_info = arizona_api.get_servers_info()
                
                # Кнопка обновления даже при ошибке
                refresh_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_servers")]
                ])
                
                await loading_msg.edit_text(
                    f"⚠️ Не удалось получить актуальный статус серверов.\n"
                    f"Показываю базовую информацию:\n\n{fallback_info}",
                    reply_markup=refresh_keyboard
                )
        
        # Admin commands for banned words
        @self.dp.message(Command("addword"), IsAdmin())
        async def add_word_command(message: Message):
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.answer("❌ Использование: /addword <слово>")
                return
            
            word = message.text.split(" ", 1)[1].lower()
            self.data_manager.add_banned_word(word)
            await message.answer(f"✅ Слово '{word}' добавлено в список запрещенных.")
        
        @self.dp.message(Command("unword"), IsAdmin())
        async def remove_word_command(message: Message):
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.answer("❌ Использование: /unword <слово>")
                return
            
            word = message.text.split(" ", 1)[1].lower()
            if self.data_manager.remove_banned_word(word):
                await message.answer(f"✅ Слово '{word}' удалено из списка запрещенных.")
            else:
                await message.answer(f"❌ Слово '{word}' не найдено в списке запрещенных.")
        
        @self.dp.message(Command("words"), IsAdmin())
        async def list_words_command(message: Message):
            words = self.data_manager.get_banned_words()
            if words:
                words_list = ", ".join(words)
                await message.answer(f"📝 <b>Запрещенные слова:</b>\n\n{words_list}", parse_mode="HTML")
            else:
                await message.answer("📝 <b>Запрещенные слова:</b>\n\nСписок пуст")
        
        # Show staff list
        @self.dp.message(Command("staff"))
        async def staff_command(message: Message):
            admin_usernames = self.data_manager.get_admin_usernames()
            if admin_usernames:
                staff_list = []
                for admin_id, username in admin_usernames.items():
                    staff_list.append(f"• @{username}")
                
                staff_text = "\n".join(staff_list)
                await message.answer(f"👥 <b>Администрация:</b>\n\n{staff_text}", parse_mode="HTML")
            else:
                await message.answer("👥Администрация:\n\nСписок пуст")

        # Admin management (Creator only)
        @self.dp.message(Command("addadmin"), IsCreator())
        async def add_admin_command(message: Message):
            if not message.reply_to_message:
                await message.answer("❌ Ответьте на сообщение пользователя, которого хотите добавить в админы.")
                return
            
            user_id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
            
            if self.data_manager.add_admin(user_id, username):
                await message.answer(f"✅ Пользователь @{username} (ID: {user_id}) добавлен в администраторы.")
            else:
                await message.answer(f"❌ Пользователь @{username} уже является администратором.")
     
        @self.dp.message(Command("unadmin"), IsCreator())
        async def remove_admin_command(message: Message):
            if not message.reply_to_message:
                await message.answer("❌ Ответьте на сообщение администратора, которого хотите удалить.")
                return
            
            user_id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
            
            if self.data_manager.remove_admin(user_id):
                await message.answer(f"✅ Пользователь {username} (ID: {user_id}) удален из администраторов.")
            else:
                await message.answer(f"❌ Пользователь {username} не является администратором.")
        
        # Bot stats (Creator only)
        @self.dp.message(Command("botstats"), IsCreator())
        async def bot_stats_command(message: Message):
            stats = f"📊 <b>Статистика бота:</b>\n\n"
            stats += f"🔄 Перезапусков: {self.restart_count}\n"
            stats += f"🤖 Платформы: Telegram"
            
            if discord_bot.is_ready:
                stats += " + Discord"
            
            stats += f"\n👥 Администраторов: {len(self.data_manager.get_admins())}\n"
            stats += f"🚫 Запрещенных слов: {len(self.data_manager.get_banned_words())}\n\n"
            
            # Информация о режиме работы
            stats += f"⏰ <b>Режим работы:</b> Непрерывный\n"
            stats += f"🔄 <b>Автоперезапуск:</b> Отключен"
            
            await message.answer(stats, parse_mode="HTML")

        # Set family chat command (creator only)
        @self.dp.message(Command("setfamilychat"), IsCreator())
        async def setfamilychat_command(message: Message):
            if message.chat.type == 'private':
                await message.answer("❌ Эта команда работает только в групповых чатах.")
                return
                
            chat_id = message.chat.id
            if self.data_manager.set_family_chat_id(chat_id):
                await message.answer(
                    f"✅ Чат семьи установлен!\n"
                    f"💬 ID чата: {chat_id}\n"
                    f"📝 Идеи и заявки игроков теперь будут приходить сюда."
                )
            else:
                await message.answer("❌ Произошла ошибка при установке чата семьи.")
        
        # Banned words filter
        @self.dp.message(F.text)
        async def banned_words_filter(message: Message):
            if message.from_user.id == CREATOR_ID:
                return  # Creator is exempt from banned words filter
            
            if self.data_manager.is_admin(message.from_user.id):
                return  # Admins are exempt from banned words filter
            
            if message.text:
                banned_words = self.data_manager.get_banned_words()
                text_lower = message.text.lower()
                
                for word in banned_words:
                    if word in text_lower:
                        try:
                            await message.delete()
                            await message.answer("⚠️ Ваше сообщение содержит запрещенные слова и было удалено.")
                        except TelegramAPIError:
                            # Can't delete message (not enough permissions)
                            await message.answer("⚠️ Ваше сообщение содержит запрещенные слова.")
                        break

        # Callback query handler for refresh servers button
        @self.dp.callback_query(F.data == "refresh_servers")
        async def refresh_servers_callback(callback: CallbackQuery):
            # Показываем пользователю, что идет загрузка
            await callback.answer("🔄 Обновляю статус серверов...", show_alert=False)
            
            try:
                # Получаем актуальную информацию о серверах
                servers_info = await arizona_api.get_servers_status_from_api()
                
                # Создаем кнопку обновления снова
                refresh_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_servers")]
                ])
                
                # Обновляем сообщение с новой информацией
                await callback.message.edit_text(
                    servers_info,
                    parse_mode="Markdown",
                    reply_markup=refresh_keyboard
                )
                
            except Exception as e:
                logger.error(f"Error refreshing servers: {e}")
                # В случае ошибки показываем базовую информацию
                fallback_info = arizona_api.get_servers_info()
                
                refresh_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_servers")]
                ])
                
                await callback.message.edit_text(
                    f"⚠️ Не удалось получить актуальный статус серверов.\n"
                    f"Показываю базовую информацию:\n\n{fallback_info}",
                    reply_markup=refresh_keyboard
                )

        # Callback query handler for rank application buttons
        @self.dp.callback_query(F.data.startswith("rank_"))
        async def rank_callback_handler(callback: CallbackQuery):
            # Check if user is admin or creator
            if callback.from_user.id != CREATOR_ID and not self.data_manager.is_admin(callback.from_user.id):
                await callback.answer("❌ У вас нет прав для этого действия.", show_alert=True)
                return
            
            action, user_id = callback.data.split("_")[1], callback.data.split("_")[2]
            user_id = int(user_id)
            
            # Get user info for notification
            admin_info = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
            
            if action == "approve":
                # Send approval notification to user
                try:
                    await self.telegram_bot.send_message(
                        user_id,
                        f"🎉 <b>Поздравляем!</b>\n\n"
                        f"✅ Ваша заявка на ранг была одобрена!\n"
                        f"👤 Рассмотрел: {admin_info}",
                        parse_mode="HTML"
                    )
                    
                    # Update message
                    await callback.message.edit_caption(
                        caption=f"{callback.message.caption}\n\n✅ <b>Заявка одобрена</b>\n👤 Рассмотрел: {admin_info}",
                        parse_mode="HTML"
                    )
                    
                    await callback.answer("✅ Заявка одобрена, пользователю отправлено уведомление.")
                    
                except Exception as e:
                    logger.error(f"Error approving rank application: {e}")
                    await callback.answer("❌ Ошибка при одобрении заявки.")
                    
            elif action == "reject":
                # Send rejection notification to user
                try:
                    await self.telegram_bot.send_message(
                        user_id,
                        f"😔 <b>Заявка отклонена</b>\n\n"
                        f"❌ Ваша заявка на ранг была отклонена.\n"
                        f"👤 Рассмотрел: {admin_info}\n\n"
                        f"💡 Вы можете подать новую заявку позже.",
                        parse_mode="HTML"
                    )
                    
                    # Update message
                    await callback.message.edit_caption(
                        caption=f"{callback.message.caption}\n\n❌ <b>Заявка отклонена</b>\n👤 Рассмотрел: {admin_info}",
                        parse_mode="HTML"
                    )
                    
                    await callback.answer("❌ Заявка отклонена, пользователю отправлено уведомление.")
                    
                except Exception as e:
                    logger.error(f"Error rejecting rank application: {e}")
                    await callback.answer("❌ Ошибка при отклонении заявки.")
    
    async def set_bot_commands(self):
        """Set bot commands for BotFather menu"""
        commands = []
        for command, description in COMMAND_DESCRIPTIONS.items():
            commands.append(BotCommand(command=command, description=description))
        
        try:
            await self.telegram_bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")
    
    async def start_telegram(self):
        """Start Telegram bot"""
        try:
            logger.info("Starting Telegram bot...")
            await self.set_bot_commands()
            await self.dp.start_polling(self.telegram_bot, skip_updates=True)
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
            raise
    
    async def start_discord(self):
        """Start Discord bot if configured"""
        if discord_bot.setup():
            try:
                await discord_bot.start()
            except Exception as e:
                logger.error(f"Discord bot failed to start: {e}")
        else:
            logger.info("Discord bot not configured, running Telegram only")
    
    async def run(self):
        """Run the unified bot"""
        if not validate_config():
            logger.error("Configuration validation failed")
            return False
        
        self.restart_count += 1
        
        try:
            # Setup Telegram bot
            if not await self.setup_telegram():
                return False
            
            logger.info("🚀 Starting unified bot...")
            print("🚀 Запуск объединенного бота...")
            
            self.running = True
            
            # Create tasks for both platforms
            telegram_task = asyncio.create_task(
                self.start_telegram(), 
                name="telegram_bot"
            )
            
            discord_task = asyncio.create_task(
                self.start_discord(), 
                name="discord_bot"
            )
            
            # Start keep-alive server
            keep_alive()
            
            # Ping creator after successful start
            await self.send_ping()
            
            # Wait for both tasks
            await asyncio.gather(telegram_task, discord_task, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            return False
        finally:
            await self.cleanup()
    
    async def send_ping(self):
        """Send ping message to creator"""
        try:
            ping_msg = f"🟢 Бот запущен успешно!\n"
            ping_msg += f"🔄 Перезапуск #{self.restart_count}\n"
            ping_msg += f"📱 Платформы: Telegram"
            
            if discord_bot.setup():
                ping_msg += " + Discord"
            
            await self.telegram_bot.send_message(CREATOR_ID, ping_msg)
            logger.info("Отправка пинг-сообщения создателю")
        except Exception as e:
            logger.error(f"Failed to send ping message: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🛑 Shutting down unified bot...")
        print("🛑 Остановка объединенного бота...")
        
        self.running = False
        
        # Close Telegram bot
        if self.telegram_bot:
            try:
                await self.telegram_bot.session.close()
                logger.info("Telegram bot closed")
            except Exception as e:
                logger.error(f"Error closing Telegram bot: {e}")
        
        # Close Discord bot
        await discord_bot.close()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            print("🛑 Получен сигнал завершения, остановка ботов...")
            
            if self.running:
                asyncio.create_task(self.cleanup())
            
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point"""
    
    # Print startup banner
    print("=" * 60)
    print("🤖 MensemBot Unified - Multi-Platform Edition")
    print("📱 Telegram + Discord Support")
    print("🎮 Community Management + Arizona RP Statistics")
    print("=" * 60)
    
    # Validate configuration
    print("🔧 Проверка конфигурации...")
    if not validate_config():
        print("❌ Ошибка конфигурации. Проверьте переменные окружения.")
        sys.exit(1)
    
    print("✅ Конфигурация валидна")
    
    # Create and run bot
    bot = UnifiedBot()
    bot.setup_signal_handlers()
    
    # Restart loop
    while bot.restart_count < bot.max_restarts:
        try:
            logger.info(f"Запуск бота в режиме 24/7...")
            logger.info(f"Starting bot... (Restart #{bot.restart_count + 1})")
            logger.info(f"Bot initialization attempt {bot.restart_count + 1}/{bot.max_restarts}")
            
            success = await bot.run()
            if success:
                break
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            print("🛑 Боты остановлены пользователем")
            break
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"❌ Неожиданная ошибка: {e}")
            
            if bot.restart_count >= bot.max_restarts:
                print(f"❌ Достигнуто максимальное количество перезапусков ({bot.max_restarts})")
                sys.exit(1)
            
            # Wait before restart
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Требуется Python 3.8 или новее")
            sys.exit(1)
        
        # Run the application
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Боты остановлены")
    except SystemExit:
        pass
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)