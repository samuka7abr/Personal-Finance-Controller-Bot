import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

class GoogleSheetsManager:
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scope)
        self.client = gspread.authorize(credentials)

        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.sheet_name = os.getenv('GOOGLE_SHEET_NAME')
        self.spreadsheet = self.client.open_by_key(self.sheet_id)
        self.worksheet = self.spreadsheet.worksheet(self.sheet_name)

        self.tz = pytz.timezone('America/Sao_Paulo')
        self._initialize_headers()

    def _initialize_headers(self):
        try:
            headers = self.worksheet.row_values(1)
            if not headers:
                self.worksheet.append_row([
                    'Data e Hora', 'Valor (R$)', 'Tipo de pagamento', 
                    'Categoria', 'Descrição', 'Créditos', 'Investimento', 'Categoria Investimento'
                ])
            elif len(headers) < 8:
                expected_headers = [
                    'Data e Hora', 'Valor (R$)', 'Tipo de pagamento', 
                    'Categoria', 'Descrição', 'Créditos', 'Investimento', 'Categoria Investimento'
                ]
                for i, header in enumerate(expected_headers, 1):
                    if i > len(headers):
                        self.worksheet.update_cell(1, i, header)
        except Exception as e:
            print(f"Erro ao inicializar cabeçalhos: {e}")

    def _normalize_text(self, text):
        return text.lower().replace(' ', '')

    def add_expense(self, valor, tipo_pagamento, categoria, descricao):
        try:
            now = datetime.now(self.tz)
            data_hora = now.strftime('%d/%m/%Y %H:%M:%S')
            tipo_pagamento = self._normalize_text(tipo_pagamento)
            categoria = self._normalize_text(categoria)
            row = [data_hora, valor, tipo_pagamento, categoria, descricao, '', '', '']
            self.worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Erro ao adicionar despesa: {e}")
            return False

    def add_credit(self, valor):
        try:
            now = datetime.now(self.tz)
            data_hora = now.strftime('%d/%m/%Y %H:%M:%S')
            row = [data_hora, '', '', '', '', valor, '', '']
            self.worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Erro ao adicionar crédito: {e}")
            return False

    def add_investment(self, valor, categoria_investimento):
        try:
            now = datetime.now(self.tz)
            data_hora = now.strftime('%d/%m/%Y %H:%M:%S')
            categoria_investimento = self._normalize_text(categoria_investimento)
            row = [data_hora, '', '', '', '', '', valor, categoria_investimento]
            self.worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Erro ao adicionar investimento: {e}")
            return False

    def clear_table(self):
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) > 1:
                self.worksheet.delete_rows(2, len(all_values))
            return True
        except Exception as e:
            print(f"Erro ao limpar tabela: {e}")
            return False

    def get_all_data(self):
        try:
            records = self.worksheet.get_all_records()
            return records
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return [] 