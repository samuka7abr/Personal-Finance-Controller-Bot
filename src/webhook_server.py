import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from .bot import create_application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return "Personal Finance Controller Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        application = create_application()
        if not application:
            return "Bot not configured", 500
        
        json_data = request.get_json()
        if json_data:
            update = Update.de_json(json_data, application.bot)
            # Executar de forma assíncrona dentro de uma função síncrona
            asyncio.run(application.process_update(update))
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return "Error", 500

def main():
    port = int(os.environ.get('PORT', 8080))
    
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    if webhook_url:
        webhook_url += '/webhook'
        
        application = create_application()
        if application:
            try:
                # Executar set_webhook de forma assíncrona
                asyncio.run(application.bot.set_webhook(webhook_url))
                logger.info(f"Webhook configurado: {webhook_url}")
            except Exception as e:
                logger.error(f"Erro ao configurar webhook: {e}")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 