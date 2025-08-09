#!/usr/bin/env python3
"""
Session Manager для предотвращения множественных запусков бота
"""

import os
import sys
import time
import logging
import atexit
from pathlib import Path

logger = logging.getLogger(__name__)

class SessionManager:
    """Управляет сессиями бота для предотвращения множественных запусков"""
    
    def __init__(self, lockfile_path: str = ".bot_session.lock"):
        self.lockfile_path = Path(lockfile_path)
        self.pid = os.getpid()
        
    def acquire_lock(self) -> bool:
        """Попытка захватить блокировку сессии"""
        try:
            if self.lockfile_path.exists():
                # Проверяем, работает ли процесс с указанным PID
                with open(self.lockfile_path, 'r') as f:
                    try:
                        old_pid = int(f.read().strip())
                        if self._is_process_running(old_pid):
                            logger.error(f"Бот уже запущен с PID {old_pid}")
                            return False
                        else:
                            logger.info(f"Найден устаревший lockfile с PID {old_pid}, удаляем")
                            self.lockfile_path.unlink()
                    except (ValueError, FileNotFoundError):
                        logger.warning("Поврежденный lockfile, удаляем")
                        self.lockfile_path.unlink()
            
            # Создаем новый lockfile
            with open(self.lockfile_path, 'w') as f:
                f.write(str(self.pid))
            
            # Регистрируем функцию очистки при завершении
            atexit.register(self.release_lock)
            
            logger.info(f"Сессия захвачена с PID {self.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при захвате блокировки: {e}")
            return False
    
    def release_lock(self):
        """Освобождение блокировки сессии"""
        try:
            if self.lockfile_path.exists():
                with open(self.lockfile_path, 'r') as f:
                    stored_pid = int(f.read().strip())
                    if stored_pid == self.pid:
                        self.lockfile_path.unlink()
                        logger.info(f"Блокировка освобождена для PID {self.pid}")
                    else:
                        logger.warning(f"PID в lockfile ({stored_pid}) не совпадает с текущим ({self.pid})")
        except Exception as e:
            logger.error(f"Ошибка при освобождении блокировки: {e}")
    
    def _is_process_running(self, pid: int) -> bool:
        """Проверка, запущен ли процесс с указанным PID"""
        try:
            # Отправляем сигнал 0 для проверки существования процесса
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def __enter__(self):
        if not self.acquire_lock():
            logger.error("Не удалось захватить блокировку сессии")
            sys.exit(1)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_lock()