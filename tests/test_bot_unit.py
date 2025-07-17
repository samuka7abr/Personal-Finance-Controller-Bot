import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestPersonalFinanceBotUnit:
    @patch('src.bot.GoogleSheetsManager')
    def setup_method(self, mock_sheets):
        mock_sheets.return_value = Mock()
        from src.bot import PersonalFinanceBotManager
        self.bot_manager = PersonalFinanceBotManager()
    
    def test_parse_expense_valid(self):
        message = "100.50 - Cartão Visa - Alimentação (supermercado)"
        result = self.bot_manager.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'despesa'
        assert result['valor'] == 100.50
        assert result['tipo_pagamento'] == 'Cartão Visa'
        assert result['categoria'] == 'Alimentação'
        assert result['descricao'] == 'supermercado'
    
    def test_parse_expense_with_comma(self):
        message = "50,00 - Dinheiro - Transporte (uber)"
        result = self.bot_manager.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'despesa'
        assert result['valor'] == 50.0
        assert result['tipo_pagamento'] == 'Dinheiro'
        assert result['categoria'] == 'Transporte'
        assert result['descricao'] == 'uber'
    
    def test_parse_credit_valid(self):
        message = "1500.00 - credito"
        result = self.bot_manager.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'credito'
        assert result['valor'] == 1500.0
    
    def test_parse_credit_with_comma(self):
        message = "2000,50 - credito"
        result = self.bot_manager.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'credito'
        assert result['valor'] == 2000.5
    
    def test_parse_investment_valid(self):
        message = "500.00 - investimento - Renda Fixa"
        result = self.bot_manager.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'investimento'
        assert result['valor'] == 500.0
        assert result['categoria_investimento'] == 'Renda Fixa'
    
    def test_parse_investment_complex_category(self):
        message = "1000,00 - investimento - Ações - Banco do Brasil"
        result = self.bot_manager.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'investimento'
        assert result['valor'] == 1000.0
        assert result['categoria_investimento'] == 'Ações - Banco do Brasil'
    
    def test_parse_invalid_format(self):
        invalid_messages = [
            "100.50 - Cartão",
            "credito - 100.50",
            "investimento - 500.00",
            "abc - Cartão - Alimentação (teste)",
            "100.50 - - Alimentação (teste)",
            ""
        ]
        
        for message in invalid_messages:
            result = self.bot_manager.parse_transaction(message)
            assert result is None, f"Mensagem '{message}' deveria ser inválida"
    
    def test_parse_edge_cases(self):
        valid_cases = [
            ("25 - Pix - Lazer (cinema)", {'tipo': 'despesa', 'valor': 25.0}),
            ("1000 - credito", {'tipo': 'credito', 'valor': 1000.0}),
            ("750 - investimento - Tesouro Direto", {'tipo': 'investimento', 'valor': 750.0}),
            ("0.99 - Cartão - Teste (mínimo)", {'tipo': 'despesa', 'valor': 0.99}),
            ("9999.99 - credito", {'tipo': 'credito', 'valor': 9999.99})
        ]
        
        for message, expected in valid_cases:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == expected['tipo']
            assert result['valor'] == expected['valor']
    
    def test_parse_whitespace_handling(self):
        cases = [
            "  100.50  -  Cartão Visa  -  Alimentação  (  supermercado  )  ",
            "100.50-Cartão Visa-Alimentação(supermercado)",
            "   1500.00   -   credito   ",
            "  500.00  -  investimento  -  Renda Fixa  "
        ]
        
        for message in cases:
            result = self.bot_manager.parse_transaction(message)
            assert result is not None

if __name__ == '__main__':
    pytest.main([__file__]) 