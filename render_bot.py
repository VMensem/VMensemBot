#!/usr/bin/env python3
"""
Render.com entry point для MensemBot
Оптимизированный для работы на Render.com с поддержкой Discord Interactions
"""

import os
import asyncio
import threading
import time
from flask import Flask
from keep_alive import app, keep_alive

# Импорт основного бота
from unified_bot import main as bot_main

def run_bot_async():
    """Запуск бота в отдельном потоке"""
    def run_bot():
        try:
            asyncio.run(bot_main())
        except Exception as e:
            print(f"❌ Ошибка бота: {e}")
            # Перезапуск бота после ошибки
            time.sleep(5)
            run_bot()
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    return bot_thread

if __name__ == "__main__":
    print("🚀 Запуск MensemBot на Render.com...")
    
    # Запуск бота в фоновом режиме
    bot_thread = run_bot_async()
    
    # Получение порта для Flask
    port = int(os.environ.get('PORT', 5000))
    
    # Запуск Flask сервера (основной процесс)
    print(f"🌐 Flask сервер запускается на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)