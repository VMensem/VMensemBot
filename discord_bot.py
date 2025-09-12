import os
import logging
import discord
from discord.ext import commands
from arizona_api import arizona_api
from unified_config import CREATOR_ID, HELP_MESSAGE_USER

logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Важно для чтения текста сообщений
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
is_ready = False

def setup():
    return DISCORD_TOKEN is not None

@bot.event
async def on_ready():
    global is_ready
    is_ready = True
    logger.info(f"Discord bot logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# Slash /help
@bot.tree.command(name="help", description="Показать справку по боту")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message(HELP_MESSAGE_USER, ephemeral=True)

# Example /stats command
@bot.tree.command(name="stats", description="Получить статистику игрока Arizona RP")
async def slash_stats(interaction: discord.Interaction, nickname: str, server_id: int):
    await interaction.response.defer()  # Отметка, что бот обрабатывает запрос
    valid_nick, nick_err = arizona_api.validate_nickname(nickname)
    valid_server, server_err = arizona_api.validate_server_id(server_id)
    if not valid_nick:
        await interaction.followup.send(f"❌ {nick_err}")
        return
    if not valid_server:
        await interaction.followup.send(f"❌ {server_err}")
        return

    data, error = await arizona_api.fetch_player_stats(nickname, server_id)
    if error:
        await interaction.followup.send(f"❌ {error}")
        return

    formatted_stats = arizona_api.format_stats(data, nickname, server_id) if data else "❌ Не удалось получить данные"
    if len(formatted_stats) > 2000:  # Discord limit
        formatted_stats = formatted_stats[:1997] + "..."
    await interaction.followup.send(formatted_stats)

# Optional: simple text command !help
@bot.command(name="help")
async def text_help(ctx):
    await ctx.send(HELP_MESSAGE_USER)

# Remove old /finish command if exists
@bot.tree.remove_command("finish", type=None)

async def close():
    await bot.close()
