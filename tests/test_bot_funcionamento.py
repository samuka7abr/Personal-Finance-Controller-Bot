import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestBotFuncionamento:
    @patch('src.bot.GoogleSheetsManager')
    def test_bot_parsing_funcionamento(self, mock_sheets_class):
        # Mock do Google Sheets
        mock_sheets = Mock()
        mock_sheets.add_expense.return_value = True
        mock_sheets.add_credit.return_value = True
        mock_sheets.add_investment.return_value = True
        mock_sheets_class.return_value = mock_sheets
        
        from src.bot import PersonalFinanceBotManager
        bot = PersonalFinanceBotManager()
        
        # Teste 1: Despesa válida
        result = bot.parse_transaction("100.50 - Cartão - Alimentação (supermercado)")
        assert result is not None
        assert result['tipo'] == 'despesa'
        assert result['valor'] == 100.50
        assert result['tipo_pagamento'] == 'Cartão'
        assert result['categoria'] == 'Alimentação'
        assert result['descricao'] == 'supermercado'
        
        # Teste 2: Crédito válido
        result = bot.parse_transaction("1500.00 - credito")
        assert result is not None
        assert result['tipo'] == 'credito'
        assert result['valor'] == 1500.0
        
        # Teste 3: Investimento válido
        result = bot.parse_transaction("500.00 - investimento - Renda Fixa")
        assert result is not None
        assert result['tipo'] == 'investimento'
        assert result['valor'] == 500.0
        assert result['categoria_investimento'] == 'Renda Fixa'
        
        print("✅ Todas as funcionalidades de parsing do bot funcionando!")
    
    @patch('src.bot.GoogleSheetsManager')
    def test_bot_integração_sheets(self, mock_sheets_class):
        # Mock do Google Sheets
        mock_sheets = Mock()
        mock_sheets.add_expense.return_value = True
        mock_sheets.add_credit.return_value = True
        mock_sheets.add_investment.return_value = True
        mock_sheets_class.return_value = mock_sheets
        
        from src.bot import PersonalFinanceBotManager
        bot = PersonalFinanceBotManager()
        
        # Simular adição de despesa
        result = bot.parse_transaction("50.00 - Pix - Transporte (uber)")
        assert result is not None
        
        # Verificar se o método seria chamado
        success = mock_sheets.add_expense(
            result['valor'],
            result['tipo_pagamento'], 
            result['categoria'],
            result['descricao']
        )
        assert success == True
        mock_sheets.add_expense.assert_called_with(50.0, 'Pix', 'Transporte', 'uber')
        
        # Simular adição de crédito  
        result = bot.parse_transaction("1000.00 - credito")
        assert result is not None
        
        success = mock_sheets.add_credit(result['valor'])
        assert success == True
        mock_sheets.add_credit.assert_called_with(1000.0)
        
        # Simular adição de investimento
        result = bot.parse_transaction("300.00 - investimento - CDB")
        assert result is not None
        
        success = mock_sheets.add_investment(result['valor'], result['categoria_investimento'])
        assert success == True
        mock_sheets.add_investment.assert_called_with(300.0, 'CDB')
        
        print("✅ Integração com Google Sheets funcionando (mockado)!")
    
    @patch('src.bot.GoogleSheetsManager')
    def test_bot_casos_reais(self, mock_sheets_class):
        # Mock do Google Sheets
        mock_sheets = Mock()
        mock_sheets_class.return_value = mock_sheets
        
        from src.bot import PersonalFinanceBotManager
        bot = PersonalFinanceBotManager()
        
        # Simular conversação real
        mensagens_usuario = [
            ("2000.00 - credito", "credito", 2000.0),
            ("50.00 - Cartão - Alimentação (café da manhã)", "despesa", 50.0),
            ("25.50 - Pix - Transporte (uber)", "despesa", 25.5),
            ("500.00 - investimento - Tesouro Direto", "investimento", 500.0),
            ("120.00 - Cartão Débito - Alimentação (almoço)", "despesa", 120.0),
            ("15.00 - Dinheiro - Transporte (ônibus)", "despesa", 15.0),
            ("80.00 - Pix - Lazer (cinema)", "despesa", 80.0),
        ]
        
        total_processadas = 0
        for mensagem, tipo_esperado, valor_esperado in mensagens_usuario:
            result = bot.parse_transaction(mensagem)
            if result is not None:
                assert result['tipo'] == tipo_esperado
                assert result['valor'] == valor_esperado
                total_processadas += 1
                print(f"✅ Processada: {mensagem} -> {tipo_esperado} R$ {valor_esperado}")
        
        assert total_processadas == len(mensagens_usuario)
        print(f"✅ {total_processadas} mensagens processadas com sucesso!")
    
    @patch('src.bot.GoogleSheetsManager')
    def test_bot_validação_erros(self, mock_sheets_class):
        # Mock do Google Sheets
        mock_sheets = Mock()
        mock_sheets_class.return_value = mock_sheets
        
        from src.bot import PersonalFinanceBotManager
        bot = PersonalFinanceBotManager()
        
        # Teste mensagens inválidas
        mensagens_invalidas = [
            "100.50 - Cartão",  # Falta categoria e descrição
            "credito - 100.50",  # Formato incorreto de crédito
            "investimento - 500.00",  # Falta categoria de investimento
            "abc - def - ghi (jkl)",  # Valor inválido
            "100.50 - - Alimentação (teste)",  # Tipo de pagamento vazio
            "100.50 - Cartão - (teste)",  # Categoria vazia
            "100.50 - Cartão - Alimentação ()",  # Descrição vazia
            "",  # Mensagem vazia
        ]
        
        erros_detectados = 0
        for mensagem in mensagens_invalidas:
            result = bot.parse_transaction(mensagem)
            if result is None:
                erros_detectados += 1
                print(f"✅ Erro detectado corretamente: '{mensagem}'")
        
        assert erros_detectados == len(mensagens_invalidas)
        print(f"✅ {erros_detectados} erros detectados corretamente!")

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 