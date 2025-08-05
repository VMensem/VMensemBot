#!/usr/bin/env python3
"""
Dual-Platform Gaming Statistics Bot
Supports both Discord and Telegram platforms
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

import discord
from discord.ext import commands
from aiogram import Bot

from config import config
from bot_handlers import DiscordBotHandlers, TelegramBotHandlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class DualPlatformBot:
    """Main application class for running both Discord and Telegram bots"""
    
    def __init__(self):
        self.discord_bot: Optional[commands.Bot] = None
        self.telegram_bot: Optional[Bot] = None
        self.telegram_handlers: Optional[TelegramBotHandlers] = None
        self.discord_handlers: Optional[DiscordBotHandlers] = None
        self.running = False
    
    def setup_discord_bot(self):
        """Initialize Discord bot"""
        try:
            # Configure Discord intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            
            # Create Discord bot instance
            self.discord_bot = commands.Bot(
                command_prefix=config.DISCORD_COMMAND_PREFIX,
                intents=intents,
                help_command=None  # We'll use custom help command
            )
            
            # Setup handlers
            self.discord_handlers = DiscordBotHandlers(self.discord_bot)
            
            logger.info("Discord bot configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Discord bot: {e}")
            raise
    
    def setup_telegram_bot(self):
        """Initialize Telegram bot"""
        try:
            # Create Telegram bot instance
            self.telegram_bot = Bot(token=config.TELEGRAM_TOKEN)
            
            # Setup handlers
            self.telegram_handlers = TelegramBotHandlers()
            
            logger.info("Telegram bot configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Telegram bot: {e}")
            raise
    
    async def start_discord_bot(self):
        """Start Discord bot"""
        try:
            logger.info("Starting Discord bot...")
            if self.discord_bot:
                await self.discord_bot.start(config.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
            raise
    
    async def start_telegram_bot(self):
        """Start Telegram bot"""
        try:
            logger.info("Starting Telegram bot...")
            if self.telegram_handlers and self.telegram_bot:
                await self.telegram_handlers.dp.start_polling(
                    self.telegram_bot,
                    skip_updates=True  # Skip pending updates on startup
                )
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
            raise
    
    async def run(self):
        """Run both bots concurrently"""
        if not config.validate():
            logger.error("Configuration validation failed")
            return False
        
        try:
            # Setup bots
            self.setup_discord_bot()
            self.setup_telegram_bot()
            
            logger.info("🚀 Starting dual-platform bot...")
            print("🚀 Запуск бота на двух платформах...")
            
            self.running = True
            
            # Create tasks for both bots
            discord_task = asyncio.create_task(
                self.start_discord_bot(), 
                name="discord_bot"
            )
            
            telegram_task = asyncio.create_task(
                self.start_telegram_bot(), 
                name="telegram_bot"
            )
            
            # Wait for both tasks
            await asyncio.gather(discord_task, telegram_task, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            return False
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🛑 Shutting down bots...")
        print("🛑 Остановка ботов...")
        
        self.running = False
        
        # Close Discord bot
        if self.discord_bot:
            try:
                await self.discord_bot.close()
                logger.info("Discord bot closed")
            except Exception as e:
                logger.error(f"Error closing Discord bot: {e}")
        
        # Close Telegram bot
        if self.telegram_bot:
            try:
                await self.telegram_bot.session.close()
                logger.info("Telegram bot closed")
            except Exception as e:
                logger.error(f"Error closing Telegram bot: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            print("🛑 Получен сигнал завершения, остановка ботов...")
            
            # Create a new event loop if needed
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Schedule cleanup
            if self.running:
                asyncio.create_task(self.cleanup())
            
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point"""
    
    # Print startup banner
    print("=" * 50)
    print("🤖 Arizona RP Statistics Bot")
    print("📱 Discord + Telegram Support")
    print("🎮 Player Statistics & Server Info")
    print("=" * 50)
    
    # Validate configuration
    print("🔧 Проверка конфигурации...")
    if not config.validate():
        print("❌ Ошибка конфигурации. Проверьте переменные окружения.")
        sys.exit(1)
    
    print("✅ Конфигурация валидна")
    
    # Create and run bot
    bot = DualPlatformBot()
    bot.setup_signal_handlers()
    
    try:
        success = await bot.run()
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("🛑 Боты остановлены пользователем")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Требуется Python 3.8 или новее")
            sys.exit(1)
        
        # Run the application
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n🛑 Боты остановлены")
    except SystemExit:
        pass
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
