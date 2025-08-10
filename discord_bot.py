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
        
        @self.bot.command(name="servers", help="Показать все серверы Arizona RP с актуальным статусом")
        async def discord_servers(ctx: commands.Context):
            """Discord servers command with real-time status"""
            # Отправляем сообщение о загрузке
            loading_embed = discord.Embed(
                title="🔄 Загрузка статуса серверов",
                description="Получаю актуальную информацию о серверах Arizona RP...",
                color=0xffaa00
            )
            message = await ctx.send(embed=loading_embed)
            
            try:
                # Получаем актуальную информацию о серверах
                servers_info = await arizona_api.get_servers_status_from_api()
                
                # Создаем embed с актуальной информацией
                embed = discord.Embed(
                    title="🌐 Arizona RP Servers",
                    description=servers_info,
                    color=0x00ff00
                )
                embed.set_footer(text="Обновлено автоматически")
                
                # Обновляем сообщение
                await message.edit(embed=embed)
                
            except Exception as e:
                logger.error(f"Error fetching servers status for Discord: {e}")
                # В случае ошибки показываем базовую информацию
                fallback_info = arizona_api.get_servers_info()
                
                error_embed = discord.Embed(
                    title="⚠️ Ошибка загрузки статуса",
                    description=f"Не удалось получить актуальный статус серверов.\nПоказываю базовую информацию:\n\n{fallback_info}",
                    color=0xff6600
                )
                
                await message.edit(embed=error_embed)
    
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