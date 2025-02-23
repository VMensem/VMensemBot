from typing import Final
import os

# Bot configuration
BOT_TOKEN: Final = os.environ.get("BOT_TOKEN")  # Token will be loaded from environment variables
CREATOR_ID: Final = 1951437901  # Creator's Telegram ID
CREATOR_USERNAME: Final = "@admin"  # Default admin username

# File paths
RULES_FILE: Final = "data/rules.json"
ADMINS_FILE: Final = "data/admins.json"
BANNED_WORDS_FILE: Final = "data/banned_words.json"

# Message templates
WELCOME_MESSAGE: Final = """
Welcome to the Moderation Bot!
Use /help to see available commands.
"""

HELP_MESSAGE: Final = """
<b>Available Commands:</b>

<b>General Commands:</b>
/start - Start the bot
/help - Show this help message
/rules - Show chat rules
/id - Show your Telegram ID

<b>Admin Commands:</b>
/setrules - Set new rules
/addword - Add banned word
/unword - Remove banned word
/stuff - Show bot statistics
/addadmin - Add new admin
/unadmin - Remove admin
"""