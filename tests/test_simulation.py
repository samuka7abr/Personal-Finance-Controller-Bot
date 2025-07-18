import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestBotSimulation:
    @patch('src.bot.GoogleSheetsManager')
    def setup_method(self, mock_sheets):
        mock_sheets.return_value = Mock()
        from src.bot import PersonalFinanceBotManager
        self.bot_manager = PersonalFinanceBotManager()
    
    def test_expense_message_simulation(self):
        test_messages = [
            "100.50 - Cartão Visa - Alimentação (supermercado)",
            "50,00 - Dinheiro - Transporte (uber)",
            "25.75 - Pix - Lazer (cinema)",
            "200 - Cartão Débito - Saúde (farmácia)",
            "15.50 - Dinheiro - Alimentação (lanche)"
        ]
        
        for message in test_messages:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == 'despesa'
    
    def test_credit_message_simulation(self):
        test_messages = [
            "1500.00 - credito",
            "2000,50 - credito", 
            "500 - credito",
            "3000.00 - credito"
        ]
        
        for message in test_messages:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == 'credito'
    
    def test_investment_message_simulation(self):
        test_messages = [
            "500.00 - investimento - Renda Fixa",
            "1000,00 - investimento - Ações",
            "750 - investimento - Tesouro Direto",
            "300.50 - investimento - CDB",
            "2000 - investimento - Fundos Imobiliários"
        ]
        
        for message in test_messages:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == 'investimento'
    
    def test_mixed_transaction_simulation(self):
        messages_and_expected = [
            ("100.50 - Cartão - Alimentação (mercado)", "despesa"),
            ("1500 - credito", "credito"),
            ("500 - investimento - Renda Fixa", "investimento"),
            ("25.75 - Pix - Transporte (uber)", "despesa"),
            ("2000,50 - credito", "credito"),
            ("300 - investimento - Ações", "investimento")
        ]
        
        for message, expected_type in messages_and_expected:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == expected_type
    
    def test_invalid_message_simulation(self):
        invalid_messages = [
            "100.50 - Cartão",
            "credito - 1500",
            "investimento - 500",
            "abc - def - ghi (jkl)",
            "- - - ()",
            "",
            "100.50",
            "Cartão - Alimentação (mercado)",
            "100.50 - - Alimentação (mercado)",
            "100.50 - Cartão - (mercado)",
            "100.50 - Cartão - Alimentação ()"
        ]
        
        for message in invalid_messages:
            result = self.bot_manager.parse_transaction(message)
            assert result is None, f"Mensagem '{message}' deveria ser inválida"
    
    def test_realistic_conversation_flow(self):
        conversation = [
            ("2000.00 - credito", "credito", 2000.0),
            ("50.00 - Cartão - Alimentação (café da manhã)", "despesa", 50.0),
            ("25.50 - Pix - Transporte (uber para trabalho)", "despesa", 25.5),
            ("500.00 - investimento - Tesouro Direto", "investimento", 500.0),
            ("120.00 - Cartão Débito - Alimentação (almoço)", "despesa", 120.0),
            ("15.00 - Dinheiro - Transporte (ônibus)", "despesa", 15.0),
            ("300.00 - investimento - CDB", "investimento", 300.0),
            ("80.00 - Pix - Lazer (cinema)", "despesa", 80.0),
            ("1000.00 - credito", "credito", 1000.0)
        ]
        
        for message, expected_type, expected_value in conversation:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == expected_type
            assert result['valor'] == expected_value
    
    def test_edge_cases_simulation(self):
        edge_cases = [
            ("0.01 - Pix - Teste (valor mínimo)", "despesa", 0.01),
            ("9999.99 - credito", "credito", 9999.99),
            ("1000000 - investimento - Imóveis", "investimento", 1000000.0),
            ("99,99 - Cartão - Alimentação (teste vírgula)", "despesa", 99.99)
        ]
        
        for message, expected_type, expected_value in edge_cases:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == expected_type
            assert result['valor'] == expected_value
    
    def test_category_variations_simulation(self):
        categories = [
            ("100 - Cartão - Alimentação (supermercado)", "Alimentação"),
            ("100 - Cartão - Transporte (uber)", "Transporte"),
            ("100 - Cartão - Saúde (farmácia)", "Saúde"),
            ("100 - Cartão - Lazer (cinema)", "Lazer"),
            ("100 - Cartão - Educação (curso)", "Educação"),
            ("100 - Cartão - Casa (material de limpeza)", "Casa"),
            ("100 - Cartão - Vestuário (roupa)", "Vestuário")
        ]
        
        for message, expected_category in categories:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == 'despesa'
            assert result['categoria'] == expected_category
    
    def test_payment_type_variations_simulation(self):
        payment_types = [
            ("100 - Cartão de Crédito - Alimentação (teste)", "Cartão de Crédito"),
            ("100 - Cartão de Débito - Alimentação (teste)", "Cartão de Débito"),
            ("100 - Pix - Alimentação (teste)", "Pix"),
            ("100 - Dinheiro - Alimentação (teste)", "Dinheiro"),
            ("100 - Transferência - Alimentação (teste)", "Transferência")
        ]
        
        for message, expected_payment in payment_types:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == 'despesa'
            assert result['tipo_pagamento'] == expected_payment
    
    def test_investment_category_variations_simulation(self):
        investment_types = [
            ("500 - investimento - Renda Fixa", "Renda Fixa"),
            ("500 - investimento - Ações", "Ações"),
            ("500 - investimento - Tesouro Direto", "Tesouro Direto"),
            ("500 - investimento - CDB", "CDB"),
            ("500 - investimento - Fundos Imobiliários", "Fundos Imobiliários"),
            ("500 - investimento - Criptomoedas", "Criptomoedas")
        ]
        
        for message, expected_category in investment_types:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == 'investimento'
            assert result['categoria_investimento'] == expected_category

if __name__ == '__main__':
    pytest.main([__file__]) 