import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
from config import (
    BOT_TOKEN, CREATOR_ID, WELCOME_MESSAGE, HELP_MESSAGE
)
from data_manager import DataManager
from keyboards import get_admin_keyboard, get_user_keyboard
from filters import IsAdmin, IsCreator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
try:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set!")
    logger.info(f"Initializing bot with token starting with: {BOT_TOKEN[:5]}...")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    data_manager = DataManager()

    logger.info("Bot and dispatcher initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    raise

# Register handlers BEFORE filters
logger.info("Registering command handlers...")

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

@dp.message(Command("setrules"))
@dp.message(IsAdmin())
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

@dp.message(Command("addword"))
@dp.message(IsAdmin())
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

@dp.message(Command("unword"))
@dp.message(IsAdmin())
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

@dp.message(Command("stuff"))
@dp.message(IsAdmin())
async def cmd_stuff(message: types.Message):
    """Handle /stuff command."""
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

@dp.message(Command("addadmin"))
@dp.message(IsCreator())
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

@dp.message(Command("unadmin"))
@dp.message(IsCreator())
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

@dp.message()
async def handle_message(message: types.Message):
    """Handle all other messages - check for banned words."""
    # Log every incoming message for debugging
    logger.debug(
        f"Received message from user {message.from_user.id}. "
        f"Text: {message.text if message.text else 'No text'}, "
        f"Command: {message.get_command() if message.is_command() else 'Not a command'}"
    )

    banned_words = data_manager.get_banned_words()
    message_text = message.text.lower() if message.text else ""

    # Skip empty messages or messages without text
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

                # Log the moderation action
                logger.info(
                    f"Deleted message from user {message.from_user.id} "
                    f"containing banned word. Chat ID: {message.chat.id}"
                )

                # Delete warning message after 30 seconds
                await asyncio.sleep(30)
                await sent_msg.delete()
            except Exception as e:
                logger.error(f"Failed to handle banned message: {e}")
            break

async def test_bot_connection():
    """Test bot connection and configuration."""
    try:
        me = await bot.get_me()
        logger.info(f"Bot connected successfully. Username: @{me.username}, ID: {me.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to bot: {e}")
        return False

# Register filters AFTER handlers
logger.info("Registering custom filters...")
dp.message.filter(IsAdmin())
dp.message.filter(IsCreator())

async def main():
    """Main function to start the bot."""
    try:
        logger.info("Starting bot...")

        # Test connection before starting
        if not await test_bot_connection():
            raise ValueError("Failed to establish connection with Telegram")

        # Start polling with clean updates
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())