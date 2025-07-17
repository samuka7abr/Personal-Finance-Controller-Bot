import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pytz
import io
import os

plt.switch_backend('Agg')
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class StatisticsGenerator:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.tz = pytz.timezone('America/Sao_Paulo')
        
        if not self.df.empty:
            self.df['Data e Hora'] = pd.to_datetime(self.df['Data e Hora'], format='%d/%m/%Y %H:%M:%S')
            
            self.df['Valor (R$)'] = self.df['Valor (R$)'].astype(str).str.replace(',', '.')
            self.df['Valor (R$)'] = pd.to_numeric(self.df['Valor (R$)'], errors='coerce').fillna(0)
            
            if 'Créditos' in self.df.columns:
                self.df['Créditos'] = self.df['Créditos'].astype(str).str.replace(',', '.')
                self.df['Créditos'] = pd.to_numeric(self.df['Créditos'], errors='coerce').fillna(0)
            else:
                self.df['Créditos'] = 0
            
            if 'Investimento' in self.df.columns:
                self.df['Investimento'] = self.df['Investimento'].astype(str).str.replace(',', '.')
                self.df['Investimento'] = pd.to_numeric(self.df['Investimento'], errors='coerce').fillna(0)
            else:
                self.df['Investimento'] = 0
            
            self.df['Data'] = self.df['Data e Hora'].dt.date
            
            self.debitos = self.df[self.df['Valor (R$)'] > 0].copy()
            self.creditos = self.df[self.df['Créditos'] > 0].copy()
            self.investimentos = self.df[self.df['Investimento'] > 0].copy()
        else:
            self.debitos = pd.DataFrame()
            self.creditos = pd.DataFrame()
            self.investimentos = pd.DataFrame()
    
    def _save_plot(self, fig, filename):
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        return buffer
    
    def gastos_por_categoria(self):
        if self.debitos.empty:
            return None
            
        gastos_categoria = self.debitos.groupby('Categoria')['Valor (R$)'].sum().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        gastos_categoria.plot(kind='barh', ax=ax, color='skyblue')
        
        ax.set_title('Gastos por Categoria', fontsize=16, fontweight='bold')
        ax.set_xlabel('Valor (R$)', fontsize=12)
        ax.set_ylabel('Categoria', fontsize=12)
        
        for i, v in enumerate(gastos_categoria.values):
            ax.text(v + max(gastos_categoria.values) * 0.01, i, f'R$ {v:.2f}', 
                   verticalalignment='center', fontweight='bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'gastos_por_categoria.png')
    
    def tipo_pagamento_mais_usado(self):
        if self.debitos.empty:
            return None
            
        pagamentos = self.debitos['Tipo de pagamento'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(pagamentos)))
        
        wedges, texts, autotexts = ax.pie(pagamentos.values, labels=pagamentos.index, 
                                         autopct='%1.1f%%', startangle=90, colors=colors)
        
        ax.set_title('Tipos de Pagamento Mais Usados', fontsize=16, fontweight='bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'tipo_pagamento.png')
    
    def investimentos_por_categoria(self):
        if self.investimentos.empty:
            return None
            
        invest_categoria = self.investimentos.groupby('Categoria Investimento')['Investimento'].sum().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        invest_categoria.plot(kind='barh', ax=ax, color='lightgreen')
        
        ax.set_title('Investimentos por Categoria', fontsize=16, fontweight='bold')
        ax.set_xlabel('Valor (R$)', fontsize=12)
        ax.set_ylabel('Categoria', fontsize=12)
        
        for i, v in enumerate(invest_categoria.values):
            ax.text(v + max(invest_categoria.values) * 0.01, i, f'R$ {v:.2f}', 
                   verticalalignment='center', fontweight='bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'investimentos_por_categoria.png')
    
    def total_gasto_mes(self):
        if self.debitos.empty:
            return None
            
        self.debitos['Mes_Ano'] = self.debitos['Data e Hora'].dt.to_period('M')
        gastos_mes = self.debitos.groupby('Mes_Ano')['Valor (R$)'].sum()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        gastos_mes.plot(kind='bar', ax=ax, color='lightcoral')
        
        ax.set_title('Total Gasto por Mês', fontsize=16, fontweight='bold')
        ax.set_xlabel('Mês/Ano', fontsize=12)
        ax.set_ylabel('Valor (R$)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        
        for i, v in enumerate(gastos_mes.values):
            ax.text(i, v + max(gastos_mes.values) * 0.01, f'R$ {v:.2f}', 
                   horizontalalignment='center', fontweight='bold')
        
        plt.tight_layout()
        return self._save_plot(fig, 'total_gasto_mes.png')
    
    def gastos_por_dia(self):
        if self.debitos.empty:
            return None
            
        gastos_dia = self.debitos.groupby('Data')['Valor (R$)'].sum().sort_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        gastos_dia.plot(kind='line', ax=ax, marker='o', linewidth=2, markersize=6, color='purple')
        
        ax.set_title('Gastos por Dia', fontsize=16, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Valor (R$)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return self._save_plot(fig, 'gastos_por_dia.png')
    
    def fluxo_financeiro(self):
        total_creditos = self.df['Créditos'].sum()
        total_debitos = self.df['Valor (R$)'].sum()
        total_investimentos = self.df['Investimento'].sum()
        
        if total_creditos == 0 and total_debitos == 0 and total_investimentos == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        categories = ['Créditos', 'Débitos', 'Investimentos']
        values = [total_creditos, total_debitos, total_investimentos]
        colors = ['green', 'red', 'blue']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        
        ax.set_title('Fluxo Financeiro: Créditos vs Débitos vs Investimentos', fontsize=16, fontweight='bold')
        ax.set_ylabel('Valor (R$)', fontsize=12)
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                   f'R$ {value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        saldo_liquido = total_creditos - total_debitos - total_investimentos
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax.text(1, max(values) * 0.9, f'Saldo Líquido: R$ {saldo_liquido:.2f}', 
               ha='center', va='bottom', fontweight='bold', 
               color='green' if saldo_liquido >= 0 else 'red', fontsize=14)
        
        plt.tight_layout()
        return self._save_plot(fig, 'fluxo_financeiro.png')
    
    def evolucao_patrimonio(self):
        if self.df.empty:
            return None
        
        df_sorted = self.df.sort_values('Data e Hora')
        
        df_sorted['Creditos_Acum'] = df_sorted['Créditos'].cumsum()
        df_sorted['Debitos_Acum'] = df_sorted['Valor (R$)'].cumsum()
        df_sorted['Investimentos_Acum'] = df_sorted['Investimento'].cumsum()
        df_sorted['Patrimonio'] = df_sorted['Creditos_Acum'] - df_sorted['Debitos_Acum'] - df_sorted['Investimentos_Acum']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(df_sorted['Data e Hora'], df_sorted['Patrimonio'], 
               marker='o', linewidth=2, markersize=4, color='blue', label='Patrimônio Líquido')
        ax.plot(df_sorted['Data e Hora'], df_sorted['Investimentos_Acum'], 
               marker='s', linewidth=2, markersize=4, color='green', label='Investimentos Acumulados')
        
        ax.set_title('Evolução do Patrimônio ao Longo do Tempo', fontsize=16, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Valor (R$)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return self._save_plot(fig, 'evolucao_patrimonio.png')
    
    def generate_all_statistics(self):
        stats = {}
        
        stats['gastos_por_categoria'] = self.gastos_por_categoria()
        stats['tipo_pagamento'] = self.tipo_pagamento_mais_usado()
        stats['investimentos_por_categoria'] = self.investimentos_por_categoria()
        stats['total_gasto_mes'] = self.total_gasto_mes()
        stats['gastos_por_dia'] = self.gastos_por_dia()
        stats['fluxo_financeiro'] = self.fluxo_financeiro()
        stats['evolucao_patrimonio'] = self.evolucao_patrimonio()
        
        return {k: v for k, v in stats.items() if v is not None}
    
    def get_summary_text(self):
        if self.df.empty:
            return "Nenhum dado encontrado para gerar estatísticas."
        
        total_creditos = self.df['Créditos'].sum()
        total_debitos = self.df['Valor (R$)'].sum()
        total_investimentos = self.df['Investimento'].sum()
        saldo_liquido = total_creditos - total_debitos - total_investimentos
        
        total_transacoes = len(self.df)
        num_creditos = len(self.creditos)
        num_debitos = len(self.debitos)
        num_investimentos = len(self.investimentos)
        
        data_inicio = self.df['Data e Hora'].min().strftime('%d/%m/%Y')
        data_fim = self.df['Data e Hora'].max().strftime('%d/%m/%Y')
        
        if not self.debitos.empty:
            categoria_freq = self.debitos['Categoria'].mode()[0] if len(self.debitos['Categoria'].mode()) > 0 else "N/A"
        else:
            categoria_freq = "N/A"
        
        if not self.investimentos.empty:
            invest_categoria_freq = self.investimentos['Categoria Investimento'].mode()[0] if len(self.investimentos['Categoria Investimento'].mode()) > 0 else "N/A"
        else:
            invest_categoria_freq = "N/A"
        
        summary = f"""📊 **RESUMO FINANCEIRO PESSOAL**
        
💰 **Total de créditos**: R$ {total_creditos:.2f} ({num_creditos} transações)
💸 **Total de débitos**: R$ {total_debitos:.2f} ({num_debitos} transações)
📈 **Total investido**: R$ {total_investimentos:.2f} ({num_investimentos} transações)
💳 **Saldo líquido**: R$ {saldo_liquido:.2f}
📊 **Total de transações**: {total_transacoes}
📅 **Período**: {data_inicio} a {data_fim}

🏷️ **Categoria de gasto mais frequente**: {categoria_freq}
📊 **Categoria de investimento mais frequente**: {invest_categoria_freq}
"""
        
        return summary 