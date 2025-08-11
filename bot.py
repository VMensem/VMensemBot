#!/usr/bin/env python3
"""
Main entry point for the unified MensemBot
Supports both Telegram and Discord platforms with Arizona RP statistics
"""

import asyncio
import sys
import signal
import logging

# Import managers and unified bot
from unified_bot import UnifiedBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_bot():
    """Запуск бота без автоматического перезапуска"""
    # Создаем основной бот
    bot = UnifiedBot()
    bot.setup_signal_handlers()

    # Обработка сигналов для корректной остановки
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}, останавливаем бота...")
        asyncio.create_task(bot.cleanup())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Запускаем бота
        await bot.run()

    except Exception as e:
        logger.error(f"Ошибка в главном цикле: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 MensemBot - Запускается")
    print("📱 Telegram + Discord")
    print("🔄 Без автоматического перезапуска")
    print("=" * 60)

    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except SystemExit as e:
        print(f"🛑 Бот завершен с кодом {e.code}")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
