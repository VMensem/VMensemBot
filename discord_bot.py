import os
import logging
import discord
from discord.ext import commands
from arizona_api import arizona_api
from unified_config import CREATOR_ID, HELP_MESSAGE_USER

# ---------------- LOGGING ---------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- CONFIG ---------------- #
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Token через environment variable
is_ready = False

# ---------------- BOT SETUP ---------------- #
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def setup():
    return DISCORD_TOKEN is not None

# ---------------- EVENTS ---------------- #
@bot.event
async def on_ready():
    global is_ready
    is_ready = True
    logger.info(f"Discord bot logged in as {bot.user}")
    try:
        synced = await tree.sync()  # глобальная синхронизация всех слеш-команд
        logger.info(f"Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# ---------------- SLASH COMMANDS ---------------- #
@tree.command(name="help", description="Показать справку по боту")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message(HELP_MESSAGE_USER, ephemeral=True)

@tree.command(name="stats", description="Получить статистику игрока Arizona RP")
async def slash_stats(interaction: discord.Interaction, nickname: str, server_id: int):
    await interaction.response.defer()
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
    if len(formatted_stats) > 2000:
        formatted_stats = formatted_stats[:1997] + "..."
    await interaction.followup.send(formatted_stats)

@tree.command(name="about", description="Информация о боте")
async def slash_about(interaction: discord.Interaction):
    about_text = (
        f"🤖 **MensemBot**\n"
        f"Создатель: vladlotto/Mensem\n"
        f"Функции: Статистика Arizona RP, помощь и справка\n"
        f"Команды: /help, /stats, /about, /servers"
    )
    await interaction.response.send_message(about_text, ephemeral=True)

@tree.command(name="servers", description="Список доступных серверов Arizona RP")
async def slash_servers(interaction: discord.Interaction):
    servers_list = "\n".join([f"{sid} — {name}" for sid, name in arizona_api.get_servers().items()])
    await interaction.response.send_message(f"Доступные серверы:\n{servers_list}", ephemeral=True)

# ---------------- OPTIONAL TEXT COMMAND ---------------- #
@bot.command(name="help")
async def text_help(ctx):
    await ctx.send(HELP_MESSAGE_USER)

# ---------------- CLEANUP ---------------- #
@bot.tree.remove_command("finish", type=None)

# ---------------- RUN BOT ---------------- #
if __name__ == "__main__":
    if not setup():
        logger.error("❌ DISCORD_TOKEN не найден! Установите переменную окружения.")
    else:
        bot.run(DISCORD_TOKEN)
