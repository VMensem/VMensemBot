import logging
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
import asyncio
from datetime import datetime
import threading
import time
from aiohttp import web
from config import (
    BOT_TOKEN, CREATOR_ID, WELCOME_MESSAGE, HELP_MESSAGE,
    RANK_MESSAGE, ADMIN_PANEL_MESSAGE, CREATOR_USERNAME, WORDS_MESSAGE, SHOP_HELP_MESSAGE, MANAGEMENT_CHAT_ID
)
from data_manager import DataManager
from keyboards import get_admin_keyboard, get_user_keyboard
from filters import IsAdmin, IsCreator
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
MAX_RECONNECT_ATTEMPTS = 5
RECONNECT_TIMEOUT = 5

async def create_bot_instance():
    """Create bot instance with reconnection logic."""
    attempt = 0
    while attempt < MAX_RECONNECT_ATTEMPTS:
        try:
            if not BOT_TOKEN:
                raise ValueError("BOT_TOKEN is not set!")

            logger.info(f"Bot initialization attempt {attempt + 1}/{MAX_RECONNECT_ATTEMPTS}")
            logger.info(f"Bot initialization at {datetime.now()}")

            bot = Bot(
                token=BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            await bot.get_me()  # Test connection
            logger.info("Bot successfully connected to Telegram")
            return bot

        except Exception as e:
            attempt += 1
            logger.error(f"Failed to initialize bot (attempt {attempt}/{MAX_RECONNECT_ATTEMPTS}): {e}")
            if attempt < MAX_RECONNECT_ATTEMPTS:
                logger.info(f"Retrying in {RECONNECT_TIMEOUT} seconds...")
                await asyncio.sleep(RECONNECT_TIMEOUT)
            else:
                raise

try:
    bot = None
    dp = Dispatcher()
    data_manager = DataManager()
    logger.info("Dispatcher and DataManager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize core components: {e}")
    raise

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command."""
    try:
        user_id = message.from_user.id
        is_creator = user_id == CREATOR_ID

        # First try without keyboard
        await message.reply(WELCOME_MESSAGE)
        logger.info(f"Sent initial welcome message to user {user_id}")

        # Now try to create and send keyboard
        try:
            keyboard = get_admin_keyboard() if is_creator else get_user_keyboard()
            logger.debug(f"Created keyboard for user {user_id} (Creator: {is_creator})")
            await message.reply("Вот доступные вам команды:", reply_markup=keyboard)
            logger.info(f"Successfully sent keyboard to user {user_id}")
        except Exception as keyboard_error:
            logger.error(f"Keyboard creation error for user {user_id}: {keyboard_error}", exc_info=True)
            # Continue without keyboard if it fails
            pass

    except Exception as e:
        logger.error(f"Critical error in start command for user {message.from_user.id}: {e}", exc_info=True)
        await message.reply("Извините, произошла ошибка при обработке команды.")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command."""
    logger.info(f"Help command received from user {message.from_user.id}")
    await message.reply(HELP_MESSAGE)

@dp.message(Command("rules"))
async def cmd_rules(message: types.Message):
    """Handle /rules command."""
    logger.info(f"Rules command received from user {message.from_user.id}")
    rules = data_manager.get_rules()
    await message.reply(f"<b>Правила Чата:</b>\n\n{rules}")

@dp.message(Command("setrules"), IsAdmin())
async def cmd_setrules(message: types.Message):
    """Handle /setrules command."""
    new_rules = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    if not new_rules:
        await message.reply("Пожалуйста, укажите текст правил после команды.")
        return

    if data_manager.set_rules(new_rules):
        await message.reply("Правила успешно обновлены!")
    else:
        await message.reply("Не удалось обновить правила.")

@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    """Handle /id command."""
    await message.reply(f"Ваш Telegram ID: <code>{message.from_user.id}</code>")

@dp.message(Command("addword"), IsAdmin())
async def cmd_addword(message: types.Message):
    """Handle /addword command."""
    word = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else ""
    if not word:
        await message.reply("Пожалуйста, укажите слово для запрета.")
        return

    if data_manager.add_banned_word(word):
        await message.reply(f"Слово '{word}' добавлено в список запрещенных.")
    else:
        await message.reply("Слово уже в списке запрещенных или не удалось добавить.")

@dp.message(Command("unword"), IsAdmin())
async def cmd_unword(message: types.Message):
    """Handle /unword command."""
    word = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else ""
    if not word:
        await message.reply("Пожалуйста, укажите слово для разблокировки.")
        return

    if data_manager.remove_banned_word(word):
        await message.reply(f"Слово '{word}' удалено из списка запрещенных.")
    else:
        await message.reply("Слово не найдено в списке или не удалось удалить.")

@dp.message(Command("staff"))
async def cmd_staff(message: types.Message):
    """Handle /staff command."""
    try:
        admins = data_manager.get_admins()
        admin_count = len(admins)
        
        # Получение юзернеймов администраторов
        admin_usernames = []
        for admin_id in admins:
            try:
                # Попытка получить информацию о пользователе
                user = await bot.get_chat(admin_id)
                username = f"@{user.username}" if user.username else f"ID: {admin_id}"
                admin_usernames.append(f"• {username}")
            except Exception:
                # Если не удалось получить информацию, используем ID
                admin_usernames.append(f"• ID: {admin_id}")
        
        admin_list = "\n".join(admin_usernames)
        
        staff_info = (
            "<b>Информация о Персонале:</b>\n\n"
            f"Всего администраторов: {admin_count}\n"
            f"Создатель бота: {CREATOR_USERNAME}\n\n"
            "<b>Список администраторов:</b>\n"
            f"{admin_list}\n\n"
            "По всем вопросам обращайтесь к администраторам."
        )

        await message.reply(staff_info)
    except Exception as e:
        logger.error(f"Error in staff command: {e}")
        await message.reply("Произошла ошибка при получении информации о персонале. Попробуйте позже.")

@dp.message(Command("stats"), IsCreator())
async def cmd_stats(message: types.Message):
    """Handle /stats command for creator only."""
    try:
        admins = data_manager.get_admins()
        banned_words = data_manager.get_banned_words()

        stats = (
            "<b>Статистика Бота:</b>\n"
            f"Количество администраторов: {len(admins)}\n"
            f"Количество запрещенных слов: {len(banned_words)}\n"
            f"\n<b>Список Администраторов:</b>\n"
            + "\n".join(f"• <code>{admin_id}</code>" for admin_id in admins)
            + f"\n\n<b>Текущие Правила:</b>\n{data_manager.get_rules()}"
        )
        await message.reply(stats)
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply("Произошла ошибка при получении статистики. Попробуйте позже.")

@dp.message(Command("addadmin"), IsCreator())
async def cmd_addadmin(message: types.Message):
    """Handle /addadmin command."""
    try:
        admin_id = int(message.text.split()[1]) if len(message.text.split()) > 1 else None
        if not admin_id:
            raise ValueError
        if data_manager.add_admin(admin_id):
            await message.reply(f"Пользователь с ID {admin_id} добавлен как администратор.")
        else:
            await message.reply("Пользователь уже администратор или не удалось добавить.")
    except ValueError:
        await message.reply("Пожалуйста, укажите корректный ID пользователя.")

@dp.message(Command("unadmin"), IsCreator())
async def cmd_unadmin(message: types.Message):
    """Handle /unadmin command."""
    try:
        admin_id = int(message.text.split()[1]) if len(message.text.split()) > 1 else None
        if not admin_id:
            raise ValueError
        if admin_id == CREATOR_ID:
            await message.reply("Невозможно удалить создателя бота!")
            return

        if data_manager.remove_admin(admin_id):
            await message.reply(f"Пользователь с ID {admin_id} удален из администраторов.")
        else:
            await message.reply("Пользователь не является администратором или не удалось удалить.")
    except ValueError:
        await message.reply("Пожалуйста, укажите корректный ID пользователя.")

@dp.message(Command("rank"))
async def cmd_rank(message: types.Message):
    """Handle /rank command."""
    logger.info(f"Rank command received from user {message.from_user.id}")
    rank_message = data_manager.get_rank_message()
    await message.reply(rank_message)

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    """Handle /info command."""
    try:
        logger.info(f"Info command received from user {message.from_user.id}")
        info = data_manager.get_info()
        await message.reply(info)
    except Exception as e:
        logger.error(f"Error in info command: {e}")
        await message.reply("Произошла ошибка при получении информации. Попробуйте позже.")

@dp.message(Command("setinfo"), IsAdmin())
async def cmd_setinfo(message: types.Message):
    """Handle /setinfo command."""
    try:
        new_info = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        if not new_info:
            await message.reply("Пожалуйста, укажите текст информации после команды /setinfo.")
            return

        if data_manager.set_info(new_info):
            await message.reply("✅ Информация успешно обновлена!")
        else:
            await message.reply("❌ Не удалось обновить информацию. Попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Error in setinfo command: {e}")
        await message.reply("Произошла ошибка при обновлении информации. Попробуйте позже.")

@dp.message(Command("ap"), IsAdmin())
async def cmd_admin_panel(message: types.Message):
    """Handle /ap command."""
    logger.info(f"Admin panel accessed by user {message.from_user.id}")
    await message.reply(ADMIN_PANEL_MESSAGE)

@dp.message(Command("setrank"), IsAdmin())
async def cmd_setrank(message: types.Message):
    """Handle /setrank command."""
    new_rank = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    if not new_rank:
        await message.reply("Пожалуйста, укажите текст информации о рангах после команды.")
        return

    if data_manager.set_rank_message(new_rank):
        await message.reply("Информация о рангах успешно обновлена!")
    else:
        await message.reply("Не удалось обновить информацию о рангах.")


@dp.message(Command("words"), IsAdmin())
async def cmd_words(message: types.Message):
    """Handle /words command - show list of banned words."""
    try:
        banned_words = data_manager.get_banned_words()
        if banned_words:
            words_list = "\n".join(f"• {word}" for word in banned_words)
            await message.reply(WORDS_MESSAGE.format(words_list))
        else:
            await message.reply("Список запрещенных слов пуст.")
    except Exception as e:
        logger.error(f"Error in words command: {e}")
        await message.reply("Произошла ошибка при получении списка слов.")

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    """Handle /shop command - submit application."""
    # Check if the command is used in private chat
    if message.chat.type != 'private':
        await message.reply("⚠️ Эта команда работает только в личных сообщениях с ботом!")
        return

    # Send application format
    await message.reply(SHOP_HELP_MESSAGE)

    # Notify creator that someone is submitting an application
    user_mention = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    await notify_creator(
        f"📝 Новая заявка\n"
        f"Пользователь: {user_mention}\n"
        f"Начал заполнение заявки."
    )

def get_application_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for application."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Выдано", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отказано", callback_data=f"reject_{user_id}")
        ]
    ])
    return keyboard

@dp.callback_query(lambda c: c.data.startswith(('approve_', 'reject_')))
async def process_application_callback(callback_query: types.CallbackQuery):
    """Handle application approval/rejection."""
    try:
        action, user_id = callback_query.data.split('_')
        user_id = int(user_id)
        is_approve = action == 'approve'

        # Update message text to show decision
        original_text = callback_query.message.text
        decision = "✅ ВЫДАНО" if is_approve else "❌ ОТКАЗАНО"
        updated_text = f"{original_text}\n\n{decision}"

        # Edit message to show decision and remove buttons
        await callback_query.message.edit_text(updated_text, parse_mode=ParseMode.HTML)

        # Notify user about decision
        try:
            status = "одобрена" if is_approve else "отклонена"
            await bot.send_message(
                user_id,
                f"Ваша заявка была {status}!"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")

        # Notify creator about decision
        await notify_creator(
            f"📝 Заявка обработана\n"
            f"Решение: {decision}\n"
            f"Пользователь ID: {user_id}"
        )

        await callback_query.answer()

    except Exception as e:
        logger.error(f"Error processing application callback: {e}")
        await callback_query.answer("Произошла ошибка при обработке заявки")

async def handle_shop_application(message: types.Message):
    """Handle shop application submissions."""
    try:
        # Get the caption from photo or video message
        if message.caption:
            text = message.caption.strip()
        else:
            await message.reply("Пожалуйста, добавьте описание к вашему фото/видео в указанном формате.")
            return False

        # Check if this is a media message with correct format
        if not (message.photo or message.video):
            await message.reply("Пожалуйста, отправьте фото или видео вместе с заявкой.")
            return False

        # Validate message format
        if not (text.startswith("Ник:") and "Ранг:" in text and "Доказательства:" in text):
            await message.reply("Пожалуйста, следуйте формату заявки:\nНик:\nРанг:\nДоказательства:")
            return False

        # If MANAGEMENT_CHAT_ID is set, forward the application
        if MANAGEMENT_CHAT_ID:
            # Create application text
            user_mention = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
            application_text = (
                f"📝 <b>Новая заявка</b>\n\n"
                f"От: {user_mention}\n\n"
                f"{text}"
            )

            # Send media with application text
            if message.photo:
                media_msg = await bot.send_photo(
                    chat_id=MANAGEMENT_CHAT_ID,
                    photo=message.photo[-1].file_id,
                    caption=application_text,
                    parse_mode=ParseMode.HTML
                )
            else:  # video
                media_msg = await bot.send_video(
                    chat_id=MANAGEMENT_CHAT_ID,
                    video=message.video.file_id,
                    caption=application_text,
                    parse_mode=ParseMode.HTML
                )

            # Send status message with buttons
            status_text = "📋 <b>Статус заявки</b>"
            await bot.send_message(
                chat_id=MANAGEMENT_CHAT_ID,
                text=status_text,
                reply_to_message_id=media_msg.message_id,
                reply_markup=get_application_keyboard(message.from_user.id),
                parse_mode=ParseMode.HTML
            )

            await message.reply("✅ Ваша заявка успешно отправлена!")
            return True

        await message.reply("⚠️ Извините, в данный момент система заявок недоступна.")
        logger.error("MANAGEMENT_CHAT_ID is not set")
        return False

    except Exception as e:
        logger.error(f"Error handling shop application: {e}")
        return False

@dp.message(Command("scripts"))
async def cmd_scripts(message: types.Message):
    """Handle /scripts command."""
    await message.reply("Скрипты были удалены из функционала бота.")

@dp.message()
async def handle_message(message: types.Message):
    """Handle all other messages - check for banned words and shop applications."""
    logger.debug(
        f"Received message from user {message.from_user.id}. "
        f"Text: {message.text if message.text else 'No text'}"
    )

    # Check if this is a shop application in private chat
    if message.chat.type == 'private' and (message.photo or message.video or message.text):
        if await handle_shop_application(message):
            return

    # Continue with banned words check
    banned_words = data_manager.get_banned_words()
    message_text = message.text.lower() if message.text else ""

    if not message_text:
        return

    for word in banned_words:
        if word in message_text:
            try:
                await message.delete()
                warning_msg = (
                    f"Сообщение от {message.from_user.get_mention(as_html=True)} удалено "
                    f"из-за использования запрещенного слова."
                )
                sent_msg = await message.answer(warning_msg)

                # Notify creator about moderation action
                await notify_creator(
                    f"🚫 Модерация: Удалено сообщение\n"
                    f"Пользователь: {message.from_user.get_mention(as_html=True)} (ID: {message.from_user.id})\n"
                    f"Чат: {message.chat.title} (ID: {message.chat.id})\n"
                    f"Причина: Запрещенное слово"
                )

                logger.info(
                    f"Deleted message from user {message.from_user.id} "
                    f"containing banned word. Chat ID: {message.chat.id}"
                )

                await asyncio.sleep(30)
                await sent_msg.delete()
            except Exception as e:
                logger.error(f"Failed to handle banned message: {e}")
            break

async def notify_creator(message: str):
    """Send notification to bot creator."""
    try:
        if bot:
            await bot.send_message(CREATOR_ID, message)
            logger.info(f"Notification sent to creator: {message}")
    except Exception as e:
        logger.error(f"Failed to send notification to creator: {e}")

async def web_server():
    """Simple web server to keep the bot alive."""
    app = web.Application()
    
    async def handle(request):
        return web.Response(text="Бот активен и работает!")
    
    app.router.add_get("/", handle)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5000)
    await site.start()
    logger.info("Web server started on port 5000")

async def main():
    """Main function to start the bot with reconnection logic."""
    # Start web server to keep the bot alive
    asyncio.create_task(web_server())
    
    # Set higher reconnection parameters for 24/7 operation
    global MAX_RECONNECT_ATTEMPTS
    MAX_RECONNECT_ATTEMPTS = 100  # Increased from 5 for better persistence
    
    restart_count = 0
    while True:
        try:
            restart_count += 1
            logger.info(f"Starting bot... (Restart #{restart_count})")
            global bot

            # Initialize bot with reconnection logic
            bot = await create_bot_instance()

            # Start polling with clean updates
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Starting polling...")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            
            # Exponential backoff for reconnection attempts
            wait_time = min(30, 5 * (restart_count % 5 + 1))
            logger.info(f"Restarting bot in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        finally:
            if bot is not None:
                try:
                    await bot.session.close()
                except:
                    pass




if __name__ == '__main__':
    # Add signal handlers to gracefully handle interruptions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        logger.info("Запуск бота в режиме 24/7...")
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Получен сигнал остановки бота.")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        logger.info("Завершение работы бота...")
        loop.close()