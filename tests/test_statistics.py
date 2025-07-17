import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.statistics import StatisticsGenerator

class TestStatisticsGenerator:
    def setup_method(self):
        self.sample_data = [
            {
                'Data e Hora': '15/01/2024 10:30:00',
                'Valor (R$)': '50.00',
                'Tipo de pagamento': 'cartaovisa',
                'Categoria': 'alimentacao',
                'Descrição': 'supermercado',
                'Créditos': '',
                'Investimento': '',
                'Categoria Investimento': ''
            },
            {
                'Data e Hora': '15/01/2024 11:00:00',
                'Valor (R$)': '',
                'Tipo de pagamento': '',
                'Categoria': '',
                'Descrição': '',
                'Créditos': '1500.00',
                'Investimento': '',
                'Categoria Investimento': ''
            },
            {
                'Data e Hora': '15/01/2024 14:00:00',
                'Valor (R$)': '',
                'Tipo de pagamento': '',
                'Categoria': '',
                'Descrição': '',
                'Créditos': '',
                'Investimento': '500.00',
                'Categoria Investimento': 'rendafixa'
            },
            {
                'Data e Hora': '16/01/2024 09:15:00',
                'Valor (R$)': '25.50',
                'Tipo de pagamento': 'pix',
                'Categoria': 'transporte',
                'Descrição': 'uber',
                'Créditos': '',
                'Investimento': '',
                'Categoria Investimento': ''
            },
            {
                'Data e Hora': '16/01/2024 16:30:00',
                'Valor (R$)': '120.00',
                'Tipo de pagamento': 'cartaodebito',
                'Categoria': 'alimentacao',
                'Descrição': 'restaurante',
                'Créditos': '',
                'Investimento': '',
                'Categoria Investimento': ''
            }
        ]
    
    def test_init_with_valid_data(self):
        stats = StatisticsGenerator(self.sample_data)
        
        assert not stats.df.empty
        assert len(stats.debitos) == 3
        assert len(stats.creditos) == 1
        assert len(stats.investimentos) == 1
    
    def test_init_with_empty_data(self):
        stats = StatisticsGenerator([])
        
        assert stats.df.empty
    
    def test_summary_text_generation(self):
        stats = StatisticsGenerator(self.sample_data)
        summary = stats.get_summary_text()
        
        assert "RESUMO FINANCEIRO PESSOAL" in summary
        assert "Total de créditos" in summary
        assert "Total de débitos" in summary
        assert "Total investido" in summary
        assert "Saldo líquido" in summary
    
    def test_summary_calculations(self):
        stats = StatisticsGenerator(self.sample_data)
        
        total_creditos = stats.df['Créditos'].sum()
        total_debitos = stats.df['Valor (R$)'].sum()
        total_investimentos = stats.df['Investimento'].sum()
        
        assert total_creditos == 1500.0
        assert total_debitos == 195.5
        assert total_investimentos == 500.0
        
        saldo_liquido = total_creditos - total_debitos - total_investimentos
        assert saldo_liquido == 804.5
    
    def test_gastos_por_categoria(self):
        stats = StatisticsGenerator(self.sample_data)
        chart_buffer = stats.gastos_por_categoria()
        
        assert chart_buffer is not None
    
    def test_tipo_pagamento_mais_usado(self):
        stats = StatisticsGenerator(self.sample_data)
        chart_buffer = stats.tipo_pagamento_mais_usado()
        
        assert chart_buffer is not None
    
    def test_investimentos_por_categoria(self):
        stats = StatisticsGenerator(self.sample_data)
        chart_buffer = stats.investimentos_por_categoria()
        
        assert chart_buffer is not None
    
    def test_fluxo_financeiro(self):
        stats = StatisticsGenerator(self.sample_data)
        chart_buffer = stats.fluxo_financeiro()
        
        assert chart_buffer is not None
    
    def test_evolucao_patrimonio(self):
        stats = StatisticsGenerator(self.sample_data)
        chart_buffer = stats.evolucao_patrimonio()
        
        assert chart_buffer is not None
    
    def test_generate_all_statistics(self):
        stats = StatisticsGenerator(self.sample_data)
        all_charts = stats.generate_all_statistics()
        
        assert isinstance(all_charts, dict)
        assert len(all_charts) > 0
        
        expected_charts = [
            'gastos_por_categoria',
            'tipo_pagamento',
            'investimentos_por_categoria',
            'fluxo_financeiro',
            'evolucao_patrimonio'
        ]
        
        for chart_name in expected_charts:
            assert chart_name in all_charts
    
    def test_empty_data_charts(self):
        empty_data = []
        stats = StatisticsGenerator(empty_data)
        
        assert stats.gastos_por_categoria() is None
        assert stats.tipo_pagamento_mais_usado() is None
        assert stats.investimentos_por_categoria() is None
    
    def test_only_expenses_data(self):
        expense_only_data = [
            {
                'Data e Hora': '15/01/2024 10:30:00',
                'Valor (R$)': '50.00',
                'Tipo de pagamento': 'cartaovisa',
                'Categoria': 'alimentacao',
                'Descrição': 'supermercado',
                'Créditos': '',
                'Investimento': '',
                'Categoria Investimento': ''
            }
        ]
        
        stats = StatisticsGenerator(expense_only_data)
        
        assert len(stats.debitos) == 1
        assert len(stats.creditos) == 0
        assert len(stats.investimentos) == 0
        
        assert stats.gastos_por_categoria() is not None
        assert stats.tipo_pagamento_mais_usado() is not None
        assert stats.investimentos_por_categoria() is None
    
    def test_data_type_conversion(self):
        stats = StatisticsGenerator(self.sample_data)
        
        assert stats.df['Valor (R$)'].dtype == 'float64'
        assert stats.df['Créditos'].dtype == 'float64'
        assert stats.df['Investimento'].dtype == 'float64'
    
    def test_date_parsing(self):
        stats = StatisticsGenerator(self.sample_data)
        
        assert stats.df['Data e Hora'].dtype == 'datetime64[ns]'
        assert len(stats.df['Data'].unique()) == 2

if __name__ == '__main__':
    pytest.main([__file__]) 