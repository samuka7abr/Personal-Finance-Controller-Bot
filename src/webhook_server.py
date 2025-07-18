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
        logger.info("Webhook recebido - processando mensagem...")
        
        application = create_application()
        if not application:
            logger.error("Application não criada - bot não configurado")
            return "Bot not configured", 500
        
        json_data = request.get_json()
        logger.info(f"Dados recebidos: {json_data}")
        
        if json_data:
            update = Update.de_json(json_data, application.bot)
            logger.info(f"Update criado: {update}")
            
            # Executar de forma assíncrona dentro de uma função síncrona
            logger.info("Processando update...")
            asyncio.run(application.process_update(update))
            logger.info("Update processado com sucesso")
        else:
            logger.warning("Nenhum dado JSON recebido")
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Erro no webhook: {e}", exc_info=True)
        return "Error", 500

def main():
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Iniciando servidor na porta: {port}")
    logger.info(f"RENDER_EXTERNAL_URL: {os.getenv('RENDER_EXTERNAL_URL')}")
    
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    if webhook_url:
        webhook_url += '/webhook'
        logger.info(f"URL do webhook completa: {webhook_url}")
        
        application = create_application()
        if application:
            try:
                # Executar set_webhook de forma assíncrona
                logger.info("Tentando configurar webhook...")
                asyncio.run(application.bot.set_webhook(webhook_url))
                logger.info(f"Webhook configurado com sucesso: {webhook_url}")
            except Exception as e:
                logger.error(f"Erro ao configurar webhook: {e}")
        else:
            logger.error("Falha ao criar application do bot")
    else:
        logger.warning("RENDER_EXTERNAL_URL não encontrada - webhook não configurado")
    
    logger.info("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 