import os
import re
import logging
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .google_sheets import GoogleSheetsManager
from .statistics import StatisticsGenerator

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PersonalFinanceBotManager:
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        
        self.expense_pattern = re.compile(
            r'^(\d+(?:[.,]\d{1,2})?)\s*-\s*([^-]+?)\s*-\s*([^-()]+?)\s*\(([^)]+)\)\s*$',
            re.IGNORECASE
        )
        
        self.credit_pattern = re.compile(
            r'^(\d+(?:[.,]\d{1,2})?)\s*-\s*credito\s*$',
            re.IGNORECASE
        )
        
        self.investment_pattern = re.compile(
            r'^(\d+(?:[.,]\d{1,2})?)\s*-\s*investimento\s*-\s*(.+?)\s*$',
            re.IGNORECASE
        )
    
    def parse_transaction(self, message_text):
        message_text = message_text.strip()
        
        credit_match = self.credit_pattern.match(message_text)
        if credit_match:
            valor_str = credit_match.group(1)
            valor_str = valor_str.replace(',', '.')
            try:
                valor = float(valor_str)
            except ValueError:
                return None
            
            return {
                'tipo': 'credito',
                'valor': valor
            }
        
        investment_match = self.investment_pattern.match(message_text)
        if investment_match:
            valor_str, categoria_investimento = investment_match.groups()
            valor_str = valor_str.replace(',', '.')
            try:
                valor = float(valor_str)
            except ValueError:
                return None
            
            if not categoria_investimento.strip():
                return None
            
            return {
                'tipo': 'investimento',
                'valor': valor,
                'categoria_investimento': categoria_investimento.strip()
            }
        
        expense_match = self.expense_pattern.match(message_text)
        if expense_match:
            valor_str, tipo_pagamento, categoria, descricao = expense_match.groups()
            
            valor_str = valor_str.replace(',', '.')
            try:
                valor = float(valor_str)
            except ValueError:
                return None
            
            if not tipo_pagamento.strip() or not categoria.strip() or not descricao.strip():
                return None
            
            return {
                'tipo': 'despesa',
                'valor': valor,
                'tipo_pagamento': tipo_pagamento.strip(),
                'categoria': categoria.strip(),
                'descricao': descricao.strip()
            }
        
        return None

bot_manager = PersonalFinanceBotManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🤖 **Bot de Controle Financeiro Pessoal**

Olá! Eu sou seu assistente financeiro pessoal.

📝 **Como usar:**

**Para despesas:**
`valor - tipo de pagamento - categoria (descrição)`

**Para créditos:**
`valor - credito`

**Para investimentos:**
`valor - investimento - categoria`

**Exemplos:**
• `100.50 - Cartão Visa - Alimentação (supermercado)`
• `50.00 - Dinheiro - Transporte (uber)`
• `1500.00 - credito`
• `500.00 - investimento - Renda Fixa`

💡 **Tipos de transação:**
• **Débitos**: Gastos normais com todas as informações
• **Créditos**: Entradas de dinheiro (formato simplificado)
• **Investimentos**: Aplicações financeiras com categoria

📊 **Comandos disponíveis:**
• /start - Mostra esta mensagem
• /statistics - Gera relatórios e gráficos completos
• /clearTable - Limpa todos os dados (cuidado!)

📈 **Relatórios incluem:**
• Resumo financeiro com saldo líquido
• Gastos por categoria
• Análise por tipo de pagamento
• Investimentos por categoria
• Evolução do patrimônio
• Fluxo financeiro completo

💡 **Dicas:**
- O valor pode usar vírgula ou ponto
- Não é obrigatório incluir centavos
- Para despesas, mantenha sempre os hífens (-) separando os campos
- A descrição deve estar entre parênteses
- Para créditos, use apenas: `valor - credito`
- Para investimentos, use: `valor - investimento - categoria`

Vamos começar a controlar suas finanças pessoais! 💰
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def clear_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        success = bot_manager.sheets_manager.clear_table()
        
        if success:
            message = "✅ Tabela limpa com sucesso! Todos os dados foram removidos."
        else:
            message = "❌ Erro ao limpar a tabela. Tente novamente."
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Erro no comando clear_table: {e}")
        await update.message.reply_text("❌ Erro interno. Tente novamente mais tarde.")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("📊 Gerando estatísticas... Por favor, aguarde.")
        
        data = bot_manager.sheets_manager.get_all_data()
        
        if not data:
            await update.message.reply_text("📈 Nenhum dado encontrado para gerar estatísticas. Adicione algumas transações primeiro!")
            return
        
        stats_gen = StatisticsGenerator(data)
        
        summary = stats_gen.get_summary_text()
        await update.message.reply_text(summary, parse_mode='Markdown')
        
        charts = stats_gen.generate_all_statistics()
        
        chart_names = {
            'gastos_por_categoria': '🏷️ Gastos por Categoria',
            'tipo_pagamento': '💳 Tipos de Pagamento',
            'investimentos_por_categoria': '📈 Investimentos por Categoria',
            'total_gasto_mes': '📅 Total Gasto por Mês',
            'gastos_por_dia': '📊 Gastos por Dia',
            'fluxo_financeiro': '💰 Fluxo Financeiro',
            'evolucao_patrimonio': '📈 Evolução do Patrimônio'
        }
        
        for chart_key, chart_buffer in charts.items():
            if chart_buffer:
                chart_buffer.seek(0)
                caption = chart_names.get(chart_key, chart_key)
                
                await update.message.reply_photo(
                    photo=InputFile(chart_buffer, filename=f'{chart_key}.png'),
                    caption=caption
                )
        
        await update.message.reply_text("✅ Relatório completo enviado!")
        
    except Exception as e:
        logger.error(f"Erro no comando statistics: {e}")
        await update.message.reply_text("❌ Erro ao gerar estatísticas. Tente novamente mais tarde.")

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        
        transaction_data = bot_manager.parse_transaction(message_text)
        
        if not transaction_data:
            await update.message.reply_text(
                "❌ Formato inválido! Use:\n\n"
                "**Para despesas:**\n"
                "`valor - tipo de pagamento - categoria (descrição)`\n"
                "Exemplo: `50.00 - Dinheiro - Transporte (uber)`\n\n"
                "**Para créditos:**\n"
                "`valor - credito`\n"
                "Exemplo: `1500.00 - credito`\n\n"
                "**Para investimentos:**\n"
                "`valor - investimento - categoria`\n"
                "Exemplo: `500.00 - investimento - Renda Fixa`",
                parse_mode='Markdown'
            )
            return
        
        if transaction_data['tipo'] == 'credito':
            success = bot_manager.sheets_manager.add_credit(transaction_data['valor'])
            if success:
                await update.message.reply_text(
                    f"✅ Crédito registrado com sucesso! ➕\n\n"
                    f"💰 Valor: R$ {transaction_data['valor']:.2f}"
                )
            else:
                await update.message.reply_text("❌ Erro ao registrar crédito. Tente novamente.")
                
        elif transaction_data['tipo'] == 'investimento':
            success = bot_manager.sheets_manager.add_investment(
                transaction_data['valor'],
                transaction_data['categoria_investimento']
            )
            if success:
                await update.message.reply_text(
                    f"✅ Investimento registrado com sucesso! 📈\n\n"
                    f"💰 Valor: R$ {transaction_data['valor']:.2f}\n"
                    f"📊 Categoria: {transaction_data['categoria_investimento']}"
                )
            else:
                await update.message.reply_text("❌ Erro ao registrar investimento. Tente novamente.")
                
        else:
            success = bot_manager.sheets_manager.add_expense(
                transaction_data['valor'],
                transaction_data['tipo_pagamento'],
                transaction_data['categoria'],
                transaction_data['descricao']
            )
            
            if success:
                await update.message.reply_text(
                    f"✅ Despesa registrada com sucesso! ➖\n\n"
                    f"💰 Valor: R$ {transaction_data['valor']:.2f}\n"
                    f"💳 Tipo: {transaction_data['tipo_pagamento']}\n"
                    f"🏷️ Categoria: {transaction_data['categoria']}\n"
                    f"📝 Descrição: {transaction_data['descricao']}"
                )
            else:
                await update.message.reply_text("❌ Erro ao registrar despesa. Tente novamente.")
    
    except Exception as e:
        logger.error(f"Erro ao processar transação: {e}")
        await update.message.reply_text("❌ Erro interno. Tente novamente mais tarde.")

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Comando não reconhecido.\n\n"
        "Use /start para ver os comandos disponíveis ou envie uma transação no formato:\n"
        "`valor - tipo de pagamento - categoria (descrição)`",
        parse_mode='Markdown'
    )

def create_application():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN não encontrado no .env")
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

def main():
    os.makedirs('logs', exist_ok=True)
    
    application = create_application()
    if not application:
        return
    
    logger.info("Bot iniciado em modo polling!")
    application.run_polling(allowed_updates=Update.ALL_TYPES) 