#!/usr/bin/env python3
"""
Main entry point for the unified MensemBot
Supports both Telegram and Discord platforms with Arizona RP statistics
Single session with automatic restart every 5 hours
"""

import asyncio
import sys
import signal
import logging

# Import managers and unified bot
from session_manager import SessionManager
from restart_scheduler import RestartScheduler
from unified_bot import main

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_with_restart_scheduler():
    """Запуск бота с планировщиком автоматического перезапуска"""
    from unified_bot import UnifiedBot
    
    # Создаем планировщик на 5 часов
    scheduler = RestartScheduler(restart_interval_hours=5)
    
    # Создаем основной бот и передаем ему планировщик
    bot = UnifiedBot()
    bot.set_scheduler(scheduler)
    bot.setup_signal_handlers()
    
    # Создаем задачу для основного бота
    bot_task = asyncio.create_task(bot.run())
    
    # Создаем задачу для планировщика
    scheduler_task = asyncio.create_task(scheduler.start())
    
    # Настраиваем callback для остановки бота при перезапуске
    async def shutdown_callback():
        logger.info("Получен сигнал остановки от планировщика")
        await bot.cleanup()
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            logger.info("Бот успешно остановлен")
    
    scheduler.set_shutdown_callback(shutdown_callback)
    
    # Обработка сигналов для корректной остановки
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}, останавливаем бота...")
        scheduler.stop()
        bot_task.cancel()
        scheduler_task.cancel()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Ждем завершения любой из задач
        done, pending = await asyncio.wait(
            [bot_task, scheduler_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Отменяем оставшиеся задачи
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
    except Exception as e:
        logger.error(f"Ошибка в главном цикле: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 MensemBot - Single Session with Auto-Restart")
    print("📱 Telegram + Discord Support")
    print("⏰ Автоматический перезапуск каждые 5 часов")
    print("=" * 60)
    
    try:
        # Используем менеджер сессий для предотвращения множественных запусков
        with SessionManager():
            logger.info("Сессия успешно захвачена, запускаем бота...")
            asyncio.run(run_with_restart_scheduler())
            
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except SystemExit as e:
        if e.code == 0:
            print("🔄 Автоматический перезапуск...")
        else:
            print(f"❌ Бот завершен с кодом {e.code}")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)