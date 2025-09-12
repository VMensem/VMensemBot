"""
Discord bot handlers for the unified MensemBot (slash-commands version)
"""

import logging
import discord
from typing import Optional
from arizona_api import arizona_api
from unified_config import DISCORD_TOKEN

logger = logging.getLogger(__name__)

class DiscordBot:
    """Discord bot with Arizona RP statistics and basic commands"""

    def __init__(self):
        self.bot: Optional[discord.Bot] = None
        self.is_ready = False

    def setup(self):
        """Setup Discord bot"""
        if not DISCORD_TOKEN:
            logger.warning("Discord token not provided, Discord bot will not start")
            return False

        try:
            intents = discord.Intents.default()
            intents.guilds = True
            intents.message_content = False  # для slash-команд не нужно

            # Pycord slash-commands bot
            self.bot = discord.Bot(intents=intents)

            self.setup_events()
            self.setup_commands()

            logger.info("Discord bot configured successfully (slash-commands)")
            return True

        except Exception as e:
            logger.error(f"Failed to setup Discord bot: {e}")
            return False

    def setup_events(self):
        @self.bot.event
        async def on_ready():
            self.is_ready = True
            logger.info(f"Discord бот запущен как {self.bot.user}")
            print(f"🤖 Discord бот запущен как {self.bot.user}")

            await self.bot.change_presence(
                activity=discord.Game(name="/stats <ник> <сервер> | /help")
            )

    def setup_commands(self):
        bot = self.bot

        @bot.slash_command(name="help", description="Показать справку по командам")
        async def help_cmd(ctx: discord.ApplicationContext):
            embed = discord.Embed(
                title="🤖 MensemBot - Справка",
                color=0x00ff00,
                description="Многофункциональный бот для Discord и Telegram"
            )
            embed.add_field(
                name="🎮 Arizona RP",
                value="`/stats <ник> <ID сервера>` - Статистика игрока\n"
                      "`/servers` - Онлайн серверов Arizona RP",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Общие команды",
                value="`/help` - Показать эту справку\n"
                      "`/about` - О боте",
                inline=False
            )
            embed.set_footer(text="Доступные серверы: ПК 1-31, Мобайл 101-103")
            await ctx.respond(embed=embed, ephemeral=True)

        @bot.slash_command(name="about", description="Информация о боте")
        async def about_cmd(ctx: discord.ApplicationContext):
            embed = discord.Embed(
                title="🤖 MensemBot",
                color=0x0099ff,
                description="Многофункциональный бот для статистики игроков Arizona RP"
            )
            embed.add_field(
                name="🔧 Функции",
                value="• Статистика игроков Arizona RP\n"
                      "• Управление сообществом\n"
                      "• Модерация чата\n"
                      "• Поддержка Discord и Telegram",
                inline=False
            )
            embed.add_field(name="👑 Создатель", value="@vladlotto", inline=True)
            embed.add_field(name="📱 Telegram", value="@mensembot", inline=True)
            embed.set_footer(text="Версия 2.0 • Discord + Telegram")
            await ctx.respond(embed=embed)

        @bot.slash_command(name="stats", description="Получить статистику игрока Arizona RP")
        async def stats_cmd(ctx: discord.ApplicationContext, nickname: str, server_id: int):
            await ctx.defer()  # покажет "думает..."
            # validate nickname
            is_valid_nick, nick_error = arizona_api.validate_nickname(nickname)
            if not is_valid_nick:
                await ctx.respond(f"❌ {nick_error}", ephemeral=True)
                return
            # validate server
            is_valid_server, server_error = arizona_api.validate_server_id(server_id)
            if not is_valid_server:
                await ctx.respond(f"❌ {server_error}", ephemeral=True)
                return
            # fetch stats
            data, error = await arizona_api.fetch_player_stats(nickname, server_id)
            if error:
                await ctx.respond(f"❌ {error}", ephemeral=True)
                return
            if data:
                formatted = arizona_api.format_stats(data, nickname, server_id)
                if len(formatted) > 2000:
                    import io
                    stats_file = io.StringIO(formatted)
                    discord_file = discord.File(fp=stats_file, filename=f"{nickname}_stats.txt")
                    await ctx.respond(
                        f"📊 Статистика {nickname} слишком большая, файл прикреплен",
                        file=discord_file
                    )
                else:
                    embed = discord.Embed(
                        title=f"📊 Статистика {nickname}",
                        color=0x00ff00,
                        description=formatted
                    )
                    await ctx.respond(embed=embed)
            else:
                await ctx.respond("❌ Не удалось получить данные", ephemeral=True)

        @bot.slash_command(name="servers", description="Показать онлайн серверов Arizona RP")
        async def servers_cmd(ctx: discord.ApplicationContext):
            await ctx.defer()
            try:
                servers_info = await arizona_api.get_servers_status_from_api()
                embed = discord.Embed(
                    title="🌐 Arizona RP Servers",
                    description=servers_info,
                    color=0x00ff00
                )
                embed.set_footer(text="Обновлено автоматически")
                await ctx.respond(embed=embed)
            except Exception as e:
                logger.error(f"Error fetching servers: {e}")
                fallback = arizona_api.get_servers_info()
                embed = discord.Embed(
                    title="⚠️ Ошибка загрузки",
                    description=f"Не удалось получить актуальный статус.\n\n{fallback}",
                    color=0xff6600
                )
                await ctx.respond(embed=embed)

    async def start(self):
        if not self.bot:
            logger.warning("Discord bot not configured, skipping start")
            return
        try:
            logger.info("Starting Discord bot...")
            await self.bot.start(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
            raise

    async def close(self):
        if self.bot:
            try:
                await self.bot.close()
                logger.info("Discord bot closed")
            except Exception as e:
                logger.error(f"Error closing Discord bot: {e}")

discord_bot = DiscordBot()
