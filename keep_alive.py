from flask import Flask, request, jsonify
from threading import Thread
import os

app = Flask('')

# Глобальная переменная для хранения Discord handler
discord_handler = None

@app.route('/')
def home():
    return "MensemBot активен и работает 24/7!"

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'MensemBot',
        'telegram': True,
        'discord_webhook': discord_handler is not None
    })

@app.route('/discord/interactions', methods=['POST'])
def discord_interactions():
    """Discord Interactions webhook endpoint"""
    if not discord_handler:
        return jsonify({'error': 'Discord handler not configured'}), 503
    
    # Получение заголовков для проверки подписи
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    
    if not signature or not timestamp:
        return jsonify({'error': 'Missing signature headers'}), 401
    
    try:
        # Получение данных взаимодействия
        interaction_data = request.json
        if not interaction_data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Простая проверка типа взаимодействия (ping)
        if interaction_data.get('type') == 1:
            return jsonify({'type': 1})  # Pong response
        
        # Ответ для остальных взаимодействий
        response = {
            'type': 4,
            'data': {
                'content': '🤖 MensemBot работает! Используйте команды Telegram бота для полной функциональности.',
                'flags': 64  # Ephemeral message
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Discord interaction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def set_discord_handler(handler):
    """Установка Discord handler"""
    global discord_handler
    discord_handler = handler

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run)
    t.start()
    return app