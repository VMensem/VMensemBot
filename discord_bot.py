import logging
from typing import Optional

# Заглушка для audioop (чтобы не падал Discord на Linux/Render)
try:
    import audioop
except ModuleNotFoundError:
    import types
    audioop = types.SimpleNamespace()
    audioop.add = lambda *a, **k: None
    audioop.mul = lambda *a, **k: None
    audioop.max = lambda *a, **k: 0

import discord
from discord import app_commands
from discord.ext import commands

from unified_config import DISCORD_TOKEN
from arizona_api import arizona_api

logger = logging.getLogger(__name__)

class DiscordBot:
    """Discord bot with Arizona RP statistics and basic commands (slash)"""
    
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

            # Создаём bot как discord.Bot для slash команд
            self.bot = discord.Bot(intents=intents)
            
            self.setup_events()
            self.setup_commands()
            
            logger.info("Discord bot configured successfully")
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
            activity = discord.Game(name="/stats <ник> <сервер> | /help")
            await self.bot.change_presence(activity=activity)

    def setup_commands(self):
        """Setup slash commands"""
        
        @self.bot.slash_command(name="help", description="Показать справку по командам")
        async def help(ctx: discord.ApplicationContext):
            embed = discord.Embed(
                title="🤖 MensemBot - Справка по командам",
                color=0x00ff00,
                description="Многофункциональный бот для Discord и Telegram"
            )
            embed.add_field(
                name="🎮 Arizona RP команды",
                value="`/stats <ник> <ID сервера>` - Статистика игрока\n"
                      "`/servers` - Все серверы Arizona RP",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Общие команды",
                value="`/help` - Показать эту справку\n"
                      "`/about` - О боте",
                inline=False
            )
            embed.add_field(
                name="📝 Примеры использования",
                value="`/stats PlayerName 1`\n`/stats Vlad_Mensem 5`",
                inline=False
            )
            embed.set_footer(text="Доступные серверы: ПК 1-31, Мобайл 101-103")
            await ctx.respond(embed=embed)

        @self.bot.slash_command(name="about", description="Информация о боте")
        async def about(ctx: discord.ApplicationContext):
            embed = discord.Embed(
                title="🤖 MensemBot",
                color=0x0099ff,
                description="Многофункциональный бот для управления сообществом и получения статистики игроков Arizona RP"
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

        @self.bot.slash_command(name="stats", description="Получить статистику игрока Arizona RP")
        async def stats(ctx: discord.ApplicationContext, nickname: str, server_id: int):
            await ctx.defer()
            
            # Validate nickname
            valid_nick, nick_err = arizona_api.validate_nickname(nickname)
            if not valid_nick:
                await ctx.respond(embed=discord.Embed(title="❌ Ошибка валидации ника", description=nick_err, color=0xff0000))
                return

            # Validate server
            valid_srv, srv_err = arizona_api.validate_server_id(server_id)
            if not valid_srv:
                await ctx.respond(embed=discord.Embed(title="❌ Ошибка валидации сервера", description=srv_err, color=0xff0000))
                return

            data, err = await arizona_api.fetch_player_stats(nickname, server_id)
            if err:
                await ctx.respond(embed=discord.Embed(title="❌ Ошибка получения данных", description=err, color=0xff0000))
                return
            
            formatted = arizona_api.format_stats(data, nickname, server_id)
            if len(formatted) > 2000:
                import io
                f = io.StringIO(formatted)
                file = discord.File(fp=f, filename=f"{nickname}_stats.txt")
                await ctx.respond(embed=discord.Embed(title=f"📊 Статистика {nickname}", description="Файл со статистикой прикреплен", color=0x00ff00), file=file)
            else:
                await ctx.respond(embed=discord.Embed(title=f"📊 Статистика {nickname}", description=formatted, color=0x00ff00))

        @self.bot.slash_command(name="servers", description="Показать все серверы Arizona RP")
        async def servers(ctx: discord.ApplicationContext):
            await ctx.defer()
            
            class RefreshView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                
                @discord.ui.button(label="🔄 Обновить", style=discord.ButtonStyle.primary)
                async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.defer()
                    try:
                        info = await arizona_api.get_servers_status_from_api()
                        embed = discord.Embed(title="🌐 Arizona RP Servers", description=info, color=0x00ff00)
                        embed.set_footer(text="Обновлено вручную")
                        await interaction.edit_original_response(embed=embed, view=RefreshView())
                    except Exception as e:
                        logger.error(f"Error refreshing servers: {e}")
                        fallback = arizona_api.get_servers_info()
                        embed = discord.Embed(title="⚠️ Ошибка", description=fallback, color=0xff6600)
                        await interaction.edit_original_response(embed=embed, view=RefreshView())

            try:
                info = await arizona_api.get_servers_status_from_api()
                embed = discord.Embed(title="🌐 Arizona RP Servers", description=info, color=0x00ff00)
                embed.set_footer(text="Обновлено автоматически • Используйте кнопку для обновления")
                await ctx.respond(embed=embed, view=RefreshView())
            except Exception as e:
                logger.error(f"Error fetching servers: {e}")
                fallback = arizona_api.get_servers_info()
                embed = discord.Embed(title="⚠️ Ошибка", description=fallback, color=0xff6600)
                await ctx.respond(embed=embed, view=RefreshView())

    async def start(self):
        if not self.bot:
            logger.warning("Discord bot not configured")
            return
        try:
            await self.bot.start(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
            raise

    async def close(self):
        if self.bot:
            await self.bot.close()
            logger.info("Discord bot closed")

discord_bot = DiscordBot()