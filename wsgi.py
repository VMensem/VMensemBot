"""
WSGI Entry Point для Render.com
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Импортируем и запускаем основной модуль бота
try:
    # Импортируем keep_alive и получаем Flask app
    from keep_alive import app
    # Импортируем основной модуль для запуска бота в фоне
    import unified_bot
    print("✅ MensemBot WSGI успешно загружен")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    # Создаем fallback Flask app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def health():
        return "MensemBot WSGI Running"
    
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "MensemBot"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)