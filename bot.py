import asyncio
import sys
import signal
import logging
from unified_bot import UnifiedBot

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_bot():
    bot = UnifiedBot()
    bot.setup_signal_handlers()

    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}, останавливаем бота...")
        asyncio.create_task(bot.cleanup())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await bot.run()

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 MensemBot - Запускается")
    print("📱 Telegram + Discord")
    print("🔄 Без автоматического перезапуска")
    print("=" * 60)

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except SystemExit as e:
        print(f"🛑 Бот завершен с кодом {e.code}")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
