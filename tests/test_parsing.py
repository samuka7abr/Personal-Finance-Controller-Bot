import pytest
import re

class MessageParser:
    def __init__(self):
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

class TestMessageParsing:
    def setup_method(self):
        self.parser = MessageParser()
    
    def test_parse_expense_valid(self):
        message = "100.50 - Cartão Visa - Alimentação (supermercado)"
        result = self.parser.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'despesa'
        assert result['valor'] == 100.50
        assert result['tipo_pagamento'] == 'Cartão Visa'
        assert result['categoria'] == 'Alimentação'
        assert result['descricao'] == 'supermercado'
    
    def test_parse_expense_with_comma(self):
        message = "50,00 - Dinheiro - Transporte (uber)"
        result = self.parser.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'despesa'
        assert result['valor'] == 50.0
        assert result['tipo_pagamento'] == 'Dinheiro'
        assert result['categoria'] == 'Transporte'
        assert result['descricao'] == 'uber'
    
    def test_parse_credit_valid(self):
        message = "1500.00 - credito"
        result = self.parser.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'credito'
        assert result['valor'] == 1500.0
    
    def test_parse_credit_with_comma(self):
        message = "2000,50 - credito"
        result = self.parser.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'credito'
        assert result['valor'] == 2000.5
    
    def test_parse_investment_valid(self):
        message = "500.00 - investimento - Renda Fixa"
        result = self.parser.parse_transaction(message)
        
        assert result is not None
        assert result['tipo'] == 'investimento'
        assert result['valor'] == 500.0
        assert result['categoria_investimento'] == 'Renda Fixa'
    
    def test_parse_investment_complex_category(self):
        message = "1000,00 - investimento - Ações - Banco do Brasil"
        result = self.parser.parse_transaction(message)
        
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
            "100.50 - Cartão - (teste)",
            "100.50 - Cartão - Alimentação ()",
            ""
        ]
        
        for message in invalid_messages:
            result = self.parser.parse_transaction(message)
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
            result = self.parser.parse_transaction(message)
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
            result = self.parser.parse_transaction(message)
            assert result is not None
    
    def test_realistic_conversation_simulation(self):
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
            result = self.parser.parse_transaction(message)
            assert result is not None
            assert result['tipo'] == expected_type
            assert result['valor'] == expected_value

if __name__ == '__main__':
    pytest.main([__file__]) 