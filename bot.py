import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
from datetime import datetime
from config import (
    BOT_TOKEN, CREATOR_ID, WELCOME_MESSAGE, HELP_MESSAGE,
    RANK_MESSAGE, ADMIN_PANEL_MESSAGE, CREATOR_USERNAME
)
from data_manager import DataManager
from keyboards import get_admin_keyboard, get_user_keyboard
from filters import IsAdmin, IsCreator

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

        staff_info = (
            "<b>Информация о Персонале:</b>\n\n"
            f"Всего администраторов: {admin_count}\n"
            f"Создатель бота: {CREATOR_USERNAME}\n\n"
            "По всем вопросам обращайтесь к администраторам."
        )

        await message.reply(staff_info)
    except Exception as e:
        logger.error(f"Error in staff command: {e}")
        await message.reply("Произошла ошибка при получении информации о персонале. Попробуйте позже.")

@dp.message(Command("stuff"), IsAdmin())
async def cmd_stuff(message: types.Message):
    """Handle /stuff command for admins."""
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
        logger.error(f"Error in stuff command: {e}")
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

@dp.message(Command("scripts"))
async def cmd_scripts(message: types.Message):
    """Handle /scripts command."""
    logger.info(f"Scripts command received from user {message.from_user.id}")
    scripts = data_manager.get_scripts()
    if scripts:
        scripts_text = "Список скриптов:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(scripts))
        await message.reply(scripts_text)
    else:
        await message.reply("Скриптов пока нет.")

@dp.message(Command("ap"), IsAdmin())
async def cmd_admin_panel(message: types.Message):
    """Handle /ap command."""
    logger.info(f"Admin panel accessed by user {message.from_user.id}")
    await message.reply(ADMIN_PANEL_MESSAGE)

@dp.message(Command("addscript"), IsAdmin())
async def cmd_addscript(message: types.Message):
    """Handle /addscript command."""
    script = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    if not script:
        await message.reply("Пожалуйста, укажите текст скрипта после команды.")
        return

    if data_manager.add_script(script):
        await message.reply("Скрипт успешно добавлен!")
    else:
        await message.reply("Не удалось добавить скрипт.")

@dp.message(Command("removescript"), IsAdmin())
async def cmd_removescript(message: types.Message):
    """Handle /removescript command."""
    scripts = data_manager.get_scripts()
    if not scripts:
        await message.reply("Скриптов нет для удаления.")
        return

    scripts_list = "Список скриптов:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(scripts))
    await message.reply(f"{scripts_list}\n\nДля удаления, используйте команду /removescript <номер>")

    try:
        index = int(message.text.split()[1]) - 1
        if 0 <= index < len(scripts):
            if data_manager.remove_script(index):
                await message.reply("Скрипт успешно удален!")
            else:
                await message.reply("Не удалось удалить скрипт.")
        else:
            await message.reply("Неверный номер скрипта.")
    except (IndexError, ValueError):
        pass

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


@dp.message()
async def handle_message(message: types.Message):
    """Handle all other messages - check for banned words."""
    logger.debug(
        f"Received message from user {message.from_user.id}. "
        f"Text: {message.text if message.text else 'No text'}"
    )

    banned_words = data_manager.get_banned_words()
    message_text = message.text.lower() if message.text else ""

    if not message_text:
        return

    for word in banned_words:
        if word in message_text:
            try:
                await message.delete()
                warning_msg = (
                    f"Сообщение от {message.from_user.mention} удалено "
                    f"из-за использования запрещенного слова."
                )
                sent_msg = await message.answer(warning_msg)

                logger.info(
                    f"Deleted message from user {message.from_user.id} "
                    f"containing banned word. Chat ID: {message.chat.id}"
                )

                await asyncio.sleep(30)
                await sent_msg.delete()
            except Exception as e:
                logger.error(f"Failed to handle banned message: {e}")
            break

async def main():
    """Main function to start the bot with reconnection logic."""
    while True:
        try:
            logger.info("Starting bot...")
            global bot

            # Initialize bot with reconnection logic
            bot = await create_bot_instance()

            # Start polling with clean updates
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Starting polling...")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            logger.info("Restarting bot in 5 seconds...")
            await asyncio.sleep(5)
        finally:
            if bot is not None:
                await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())