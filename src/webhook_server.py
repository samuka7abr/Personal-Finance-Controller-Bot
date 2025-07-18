#!/usr/bin/env python3
"""
Servidor Webhook para o Finance Controller Bot
Mantém toda a funcionalidade do bot original, apenas muda a forma de receber mensagens
"""

import os
import logging
import asyncio
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .bot import PersonalFinanceBotManager, start, clear_table, statistics, handle_transaction, handle_unknown

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
telegram_app = None
loop = None

def create_telegram_app():
    """Cria a aplicação do Telegram com os mesmos handlers do bot original"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN não encontrado")
        return None
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clearTable", clear_table))
    application.add_handler(CommandHandler("statistics", statistics))
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_transaction
    ))
    
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown))
    
    return application

def run_async_task(coro):
    """Executa uma corrotina no loop asyncio"""
    if loop and loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()

@app.route('/')
def index():
    """Página inicial informativa"""
    return """
    <h1>🤖 Personal Finance Controller Bot</h1>
    <p><strong>Status:</strong> ✅ Online (Webhook Mode)</p>
    <p><strong>Endpoints:</strong></p>
    <ul>
        <li><code>/health</code> - Health check</li>
        <li><code>/webhook</code> - Webhook do Telegram</li>
    </ul>
    <p><em>Bot funcionando em modo webhook para deploy no Render.</em></p>
    """

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para o Render saber que o serviço está ativo"""
    return jsonify({
        'status': 'healthy',
        'service': 'Personal Finance Controller Bot',
        'mode': 'webhook'
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint que recebe mensagens do Telegram via webhook"""
    try:
        logger.info("Webhook recebido - processando mensagem...")
        
        update_data = request.get_json()
        logger.info(f"Dados recebidos: {update_data}")
        
        if not update_data:
            logger.warning("Webhook chamado sem dados")
            return jsonify({'status': 'no_data'}), 400
        
        update = Update.de_json(update_data, telegram_app.bot)
        logger.info(f"Update criado: {update}")
        
        logger.info("Processando update...")
        run_async_task(telegram_app.process_update(update))
        logger.info("Update processado com sucesso")
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"Erro no webhook: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

def setup_webhook():
    """Configura o webhook automaticamente no startup"""
    try:
        render_external_url = os.getenv('RENDER_EXTERNAL_URL')
        if render_external_url:
            webhook_url = f"{render_external_url}/webhook"
            logger.info(f"Configurando webhook para: {webhook_url}")
            
            async def set_webhook_async():
                await telegram_app.bot.set_webhook(webhook_url)
                logger.info("✅ Webhook configurado com sucesso!")
            
            run_async_task(set_webhook_async())
        else:
            logger.warning("RENDER_EXTERNAL_URL não encontrada - webhook não configurado")
    
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")

def run_async_loop():
    """Executa o loop asyncio em uma thread separada"""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def init_app():
        logger.info("Inicializando aplicação do Telegram...")
        await telegram_app.initialize()
        await telegram_app.start()
        logger.info("Aplicação do Telegram inicializada com sucesso!")
    
    loop.run_until_complete(init_app())
    
    if os.getenv('RENDER'):
        setup_webhook()
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

def main():
    """Função principal que inicializa o servidor webhook"""
    global telegram_app
    
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Iniciando servidor na porta: {port}")
    logger.info(f"RENDER_EXTERNAL_URL: {os.getenv('RENDER_EXTERNAL_URL')}")
    
    os.makedirs('logs', exist_ok=True)
    
    telegram_app = create_telegram_app()
    if not telegram_app:
        logger.error("Falha ao criar aplicação do Telegram")
        return
    
    # Iniciar loop asyncio em thread separada
    async_thread = Thread(target=run_async_loop, daemon=True)
    async_thread.start()
    
    # Aguardar um pouco para garantir que a inicialização terminou
    import time
    time.sleep(3)
    
    logger.info("🚀 Servidor webhook iniciado")
    logger.info("🤖 Bot funcionando em modo webhook")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 