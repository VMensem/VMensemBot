"""
Discord bot handlers for the unified MensemBot
"""

import logging
from typing import Optional

import discord
from discord.ext import commands

from unified_config import DISCORD_TOKEN, DISCORD_COMMAND_PREFIX, validate_config
from arizona_api import arizona_api

logger = logging.getLogger(__name__)

class DiscordBot:
    """Discord bot with Arizona RP statistics and basic commands"""
    
    def __init__(self):
        self.bot: Optional[commands.Bot] = None
        self.is_ready = False
        
    def setup(self):
        """Setup Discord bot"""
        if not DISCORD_TOKEN:
            logger.warning("Discord token not provided, Discord bot will not start")
            return False
            
        try:
            # Configure Discord intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            
            # Create Discord bot instance
            self.bot = commands.Bot(
                command_prefix=DISCORD_COMMAND_PREFIX,
                intents=intents,
                help_command=None  # We'll use custom help command
            )
            
            self.setup_events()
            self.setup_commands()
            
            logger.info("Discord bot configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Discord bot: {e}")
            return False
    
    def setup_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            self.is_ready = True
            logger.info(f"Discord бот запущен как {self.bot.user}")
            print(f"🤖 Discord бот запущен как {self.bot.user}")
            
            # Set bot status
            activity = discord.Game(name="!stats <ник> <сервер> | !help")
            await self.bot.change_presence(activity=activity)
        
        @self.bot.event
        async def on_command_error(ctx: commands.Context, error: Exception):
            """Handle command errors"""
            logger.error(f"Discord command error: {error}")
            
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("❌ Команда не найдена. Используйте `!help` для списка команд.")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("❌ Неверный формат команды. Используйте `!help` для справки.")
            elif isinstance(error, commands.BadArgument):
                await ctx.send("❌ Неверные аргументы команды.")
            else:
                await ctx.send("❌ Произошла ошибка при выполнении команды.")
    
    def setup_commands(self):
        """Setup Discord bot commands"""
        
        @self.bot.command(name="help", help="Показать справку по командам")
        async def discord_help(ctx: commands.Context):
            """Discord help command"""
            embed = discord.Embed(
                title="🤖 MensemBot - Справка по командам",
                color=0x00ff00,
                description="Многофункциональный бот для Discord и Telegram"
            )
            
            embed.add_field(
                name="🎮 Arizona RP команды",
                value="`!stats <ник> <ID сервера>` - Статистика игрока\n"
                      "`!servers` - Все серверы Arizona RP",
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Общие команды",
                value="`!help` - Показать эту справку\n"
                      "`!about` - О боте",
                inline=False
            )
            
            embed.add_field(
                name="📝 Примеры использования",
                value="`!stats PlayerName 1`\n"
                      "`!stats Vlad_Mensem 5`",
                inline=False
            )
            
            embed.set_footer(text="Доступные серверы: ПК 1-31, Мобайл 101-103")
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name="about", help="Информация о боте")
        async def discord_about(ctx: commands.Context):
            """Discord about command"""
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
            
            embed.add_field(
                name="👑 Создатель",
                value="@vladlotto",
                inline=True
            )
            
            embed.add_field(
                name="📱 Telegram",
                value="@mensembot",
                inline=True
            )
            
            embed.set_footer(text="Версия 2.0 • Discord + Telegram")
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name="stats", help="Получить статистику игрока Arizona RP")
        async def discord_stats(ctx: commands.Context, nickname: str = "", server_id: int = 0):
            """Discord stats command handler"""
            
            # Show typing indicator
            async with ctx.typing():
                # Validate arguments
                if not nickname or server_id == 0:
                    embed = discord.Embed(
                        title="❌ Неверный формат команды!",
                        color=0xff0000,
                        description="**Использование:** `!stats <ник> <ID сервера>`"
                    )
                    embed.add_field(
                        name="📋 Доступные серверы",
                        value="**ПК:** 1-31\n**Мобайл:** 101-103",
                        inline=False
                    )
                    embed.add_field(
                        name="📝 Пример",
                        value="`!stats PlayerName 1`",
                        inline=False
                    )
                    embed.set_footer(text="Используйте !servers для полного списка")
                    await ctx.send(embed=embed)
                    return
                
                # Validate nickname
                is_valid_nick, nick_error = arizona_api.validate_nickname(nickname)
                if not is_valid_nick:
                    embed = discord.Embed(
                        title="❌ Ошибка валидации ника",
                        color=0xff0000,
                        description=nick_error
                    )
                    await ctx.send(embed=embed)
                    return
                
                # Validate server ID
                is_valid_server, server_error = arizona_api.validate_server_id(server_id)
                if not is_valid_server:
                    embed = discord.Embed(
                        title="❌ Ошибка валидации сервера",
                        color=0xff0000,
                        description=server_error
                    )
                    await ctx.send(embed=embed)
                    return
                
                # Fetch statistics
                data, error = await arizona_api.fetch_player_stats(nickname, server_id)
                
                if error:
                    embed = discord.Embed(
                        title="❌ Ошибка получения данных",
                        color=0xff0000,
                        description=error
                    )
                    await ctx.send(embed=embed)
                    return
                
                # Format and send response
                if data is not None:
                    formatted_stats = arizona_api.format_stats(data, nickname, server_id)
                    
                    # Split message if too long for Discord
                    if len(formatted_stats) > 2000:
                        # Send as text file if too long
                        import io
                        stats_file = io.StringIO(formatted_stats)
                        discord_file = discord.File(fp=stats_file, filename=f"{nickname}_stats.txt")
                        
                        embed = discord.Embed(
                            title=f"📊 Статистика игрока {nickname}",
                            color=0x00ff00,
                            description=f"Статистика слишком большая для отображения в сообщении.\nФайл со статистикой прикреплен."
                        )
                        await ctx.send(embed=embed, file=discord_file)
                    else:
                        embed = discord.Embed(
                            title=f"📊 Статистика игрока {nickname}",
                            color=0x00ff00,
                            description=formatted_stats
                        )
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌ Не удалось получить данные",
                        color=0xff0000,
                        description="Проверьте правильность ника и ID сервера."
                    )
                    await ctx.send(embed=embed)
        
        @self.bot.command(name="servers", help="Показать все серверы Arizona RP")
        async def discord_servers(ctx: commands.Context):
            """Discord servers command"""
            embed = discord.Embed(
                title="Серверы Arizona RP:",
                color=0x0099ff
            )
            
            # ПК серверы
            pc_servers = " 1: Phoenix\n 2: Tucson\n 3: Scottdale\n 4: Chandler\n 5: Brainburg\n 6: Saint Rose\n 7: Mesa\n 8: Red Rock\n 9: Yuma\n10: Surprise\n11: Prescott\n12: Glendale\n13: Kingman\n14: Winslow\n15: Payson\n16: Gilbert\n17: Show Low\n18: Casa Grande\n19: Page\n20: Sun City\n21: Queen Creek\n22: Sedona\n23: Holiday\n24: Wednesday\n25: Yava\n26: Faraway\n27: Bumble Bee\n28: Christmas\n29: Mirage\n30: Love\n31: Drake"
            embed.add_field(
                name="💻 ПК серверы (1-31)",
                value=pc_servers,
                inline=False
            )
            
            # Мобайл серверы
            embed.add_field(
                name="📱 Мобайл серверы",
                value="101: Mobile 1\n102: Mobile 2\n103: Mobile 3",
                inline=False
            )
            
            embed.add_field(
                name="📝 Использование",
                value="`!stats <ник> <ID сервера>`\n**Пример:** `!stats PlayerName 1`",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    async def start(self):
        """Start Discord bot"""
        if not self.bot:
            logger.warning("Discord bot not configured, skipping Discord startup")
            return
            
        try:
            logger.info("Starting Discord bot...")
            await self.bot.start(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
            raise
    
    async def close(self):
        """Close Discord bot"""
        if self.bot:
            try:
                await self.bot.close()
                logger.info("Discord bot closed")
            except Exception as e:
                logger.error(f"Error closing Discord bot: {e}")

# Global Discord bot instance
discord_bot = DiscordBot()