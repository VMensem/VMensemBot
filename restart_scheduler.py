#!/usr/bin/env python3
"""
Планировщик автоматического перезапуска бота каждые 5 часов
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class RestartScheduler:
    """Планировщик для автоматического перезапуска бота"""
    
    def __init__(self, restart_interval_hours: int = 5):
        self.restart_interval = restart_interval_hours * 3600  # конвертируем в секунды
        self.start_time = time.time()
        self.next_restart_time = self.start_time + self.restart_interval
        self.shutdown_callback: Optional[Callable] = None
        self.running = False
        
    def set_shutdown_callback(self, callback: Callable):
        """Установка функции обратного вызова для остановки бота"""
        self.shutdown_callback = callback
    
    async def start(self):
        """Запуск планировщика"""
        self.running = True
        logger.info(f"Планировщик запущен. Следующий перезапуск через {self.restart_interval // 3600} часов")
        
        # Показываем время следующего перезапуска
        next_restart = datetime.fromtimestamp(self.next_restart_time)
        logger.info(f"Следующий перезапуск: {next_restart.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while self.running:
            current_time = time.time()
            
            # Проверяем, пора ли перезапускаться
            if current_time >= self.next_restart_time:
                logger.info("⏰ Время автоматического перезапуска!")
                await self._initiate_restart()
                break
            
            # Показываем оставшееся время каждый час
            time_until_restart = self.next_restart_time - current_time
            if int(time_until_restart) % 3600 == 0 and time_until_restart > 0:
                hours_left = int(time_until_restart // 3600)
                logger.info(f"⏱️ До автоматического перезапуска: {hours_left} часов")
            
            # Спим 60 секунд перед следующей проверкой
            await asyncio.sleep(60)
    
    async def _initiate_restart(self):
        """Инициация перезапуска"""
        logger.info("🔄 Инициируем автоматический перезапуск...")
        
        if self.shutdown_callback:
            try:
                await self.shutdown_callback()
            except Exception as e:
                logger.error(f"Ошибка при вызове shutdown_callback: {e}")
        
        # Завершаем процесс для перезапуска
        logger.info("🚀 Перезапуск бота...")
        sys.exit(0)
    
    def stop(self):
        """Остановка планировщика"""
        self.running = False
        logger.info("Планировщик остановлен")
    
    def get_uptime(self) -> str:
        """Получение времени работы"""
        uptime_seconds = time.time() - self.start_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}ч {minutes}м"
    
    def get_time_until_restart(self) -> str:
        """Получение времени до следующего перезапуска"""
        time_left = self.next_restart_time - time.time()
        if time_left <= 0:
            return "Готов к перезапуску"
        
        hours = int(time_left // 3600)
        minutes = int((time_left % 3600) // 60)
        return f"{hours}ч {minutes}м"