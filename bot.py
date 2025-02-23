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
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
data_manager = DataManager()

# Register custom filters
dp.message.filter(IsAdmin)
dp.message.filter(IsCreator)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command."""
    user_id = message.from_user.id
    is_creator = user_id == CREATOR_ID
    keyboard = get_admin_keyboard() if is_creator else get_user_keyboard()
    logging.info(f"Start command received from user {user_id} (Creator: {is_creator})")
    await message.reply(WELCOME_MESSAGE, reply_markup=keyboard)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command."""
    logging.info(f"Help command received from user {message.from_user.id}")
    await message.reply(HELP_MESSAGE)

@dp.message(Command("rules"))
async def cmd_rules(message: types.Message):
    """Handle /rules command."""
    logging.info(f"Rules command received from user {message.from_user.id}")
    rules = data_manager.get_rules()
    await message.reply(f"<b>Chat Rules:</b>\n\n{rules}")

@dp.message(Command("setrules"))
@dp.message(IsAdmin())
async def cmd_setrules(message: types.Message):
    """Handle /setrules command."""
    new_rules = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    if not new_rules:
        await message.reply("Please provide rules text after the command.")
        return

    if data_manager.set_rules(new_rules):
        await message.reply("Rules updated successfully!")
    else:
        await message.reply("Failed to update rules.")

@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    """Handle /id command."""
    await message.reply(f"Your Telegram ID: <code>{message.from_user.id}</code>")

@dp.message(Command("addword"))
@dp.message(IsAdmin())
async def cmd_addword(message: types.Message):
    """Handle /addword command."""
    word = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else ""
    if not word:
        await message.reply("Please provide a word to ban.")
        return

    if data_manager.add_banned_word(word):
        await message.reply(f"Added '{word}' to banned words list.")
    else:
        await message.reply("Word already in the banned list or failed to add.")

@dp.message(Command("unword"))
@dp.message(IsAdmin())
async def cmd_unword(message: types.Message):
    """Handle /unword command."""
    word = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else ""
    if not word:
        await message.reply("Please provide a word to unban.")
        return

    if data_manager.remove_banned_word(word):
        await message.reply(f"Removed '{word}' from banned words list.")
    else:
        await message.reply("Word not found in banned list or failed to remove.")

@dp.message(Command("stuff"))
@dp.message(IsAdmin())
async def cmd_stuff(message: types.Message):
    """Handle /stuff command."""
    admins = data_manager.get_admins()
    banned_words = data_manager.get_banned_words()

    stats = (
        "<b>Bot Statistics:</b>\n"
        f"Number of admins: {len(admins)}\n"
        f"Number of banned words: {len(banned_words)}\n"
        f"\n<b>Admin List:</b>\n"
        + "\n".join(f"• <code>{admin_id}</code>" for admin_id in admins)
        + f"\n\n<b>Active Rules:</b>\n{data_manager.get_rules()}"
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
            await message.reply(f"Added user ID {admin_id} as admin.")
        else:
            await message.reply("User is already an admin or failed to add.")
    except ValueError:
        await message.reply("Please provide a valid user ID.")

@dp.message(Command("unadmin"))
@dp.message(IsCreator())
async def cmd_unadmin(message: types.Message):
    """Handle /unadmin command."""
    try:
        admin_id = int(message.text.split()[1]) if len(message.text.split()) > 1 else None
        if not admin_id:
            raise ValueError
        if admin_id == CREATOR_ID:
            await message.reply("Cannot remove the creator!")
            return

        if data_manager.remove_admin(admin_id):
            await message.reply(f"Removed user ID {admin_id} from admins.")
        else:
            await message.reply("User is not an admin or failed to remove.")
    except ValueError:
        await message.reply("Please provide a valid user ID.")

@dp.message()
async def handle_message(message: types.Message):
    """Handle all other messages - check for banned words."""
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
                    f"Message from {message.from_user.mention} deleted "
                    f"due to banned word usage."
                )
                sent_msg = await message.answer(warning_msg)

                # Log the moderation action
                logging.info(
                    f"Deleted message from user {message.from_user.id} "
                    f"containing banned word. Chat ID: {message.chat.id}"
                )

                # Delete warning message after 30 seconds
                await asyncio.sleep(30)
                await sent_msg.delete()
            except Exception as e:
                logging.error(f"Failed to handle banned message: {e}")
            break

async def main():
    """Main function to start the bot."""
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())