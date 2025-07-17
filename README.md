# 🤖 Personal Finance Controller Bot

Bot do Telegram para controle financeiro pessoal que registra despesas, créditos e investimentos no Google Sheets e gera relatórios estatísticos com gráficos.

## 📋 Funcionalidades

- ✅ Registro de despesas via mensagens no Telegram
- ✅ Registro de créditos (entradas de dinheiro)
- ✅ Registro de investimentos por categoria
- ✅ Armazenamento automático em Google Sheets
- ✅ Geração de relatórios estatísticos
- ✅ 7 tipos de gráficos diferentes
- ✅ Normalização automática de dados
- ✅ Interface amigável com emojis
- ✅ Suporte a webhook para produção

## 📊 Estrutura da Planilha

| Data e Hora | Valor (R$) | Tipo de pagamento | Categoria | Descrição | Créditos | Investimento | Categoria Investimento |
|--------------|------------|-------------------|-----------|-----------|----------|--------------|----------------------|
| 15/01/2024 10:30:00 | 50.00 | cartaovisa | alimentacao | supermercado | | | |
| 15/01/2024 11:00:00 | | | | | 1500.00 | | |
| 15/01/2024 14:00:00 | | | | | | 500.00 | rendafixa |

## 🚀 Como Usar

### Formato das Mensagens

**Para despesas:**
```
valor - tipo de pagamento - categoria (descrição)
```

**Para créditos:**
```
valor - credito
```

**Para investimentos:**
```
valor - investimento - categoria
```

### Exemplos
- `100.50 - Cartão Visa - Alimentação (supermercado)`
- `50.00 - Dinheiro - Transporte (uber)`
- `1500.00 - credito`
- `500.00 - investimento - Renda Fixa`

### Comandos Disponíveis

- `/start` - Mostra as instruções de uso
- `/statistics` - Gera relatório completo com gráficos
- `/clearTable` - Limpa todos os dados da planilha

## 📈 Gráficos Gerados

1. **Gastos por Categoria** - Gráfico de barras horizontais
2. **Tipos de Pagamento** - Gráfico de pizza
3. **Investimentos por Categoria** - Gráfico de barras horizontais
4. **Total Gasto por Mês** - Gráfico de barras verticais
5. **Gastos por Dia** - Gráfico de linha temporal
6. **Fluxo Financeiro** - Comparação créditos vs débitos vs investimentos
7. **Evolução do Patrimônio** - Linha temporal do patrimônio líquido

## ⚙️ Configuração

### 1. Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (opcional)
- Conta do Google com Google Sheets API habilitada
- Bot do Telegram criado via @BotFather

### 2. Configuração do Google Sheets

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Habilite a Google Sheets API
4. Crie uma conta de serviço:
   - Vá em "IAM & Admin" > "Service Accounts"
   - Clique em "Create Service Account"
   - Baixe o arquivo JSON das credenciais
5. Crie uma planilha no Google Sheets
6. Compartilhe a planilha com o email da conta de serviço (permissão de editor)

### 3. Configuração do Bot do Telegram

1. Acesse [@BotFather](https://t.me/botfather) no Telegram
2. Use o comando `/newbot`
3. Siga as instruções para criar seu bot
4. Anote o token do bot

### 4. Configuração do Ambiente

Edite o arquivo `.env`:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
GOOGLE_SHEET_ID=id_da_sua_planilha
GOOGLE_SHEET_NAME=nome_da_aba
GOOGLE_SERVICE_ACCOUNT_FILE=config/credentials.json
```

Coloque o arquivo JSON das credenciais em `config/credentials.json`

## 🏃‍♂️ Execução

### Desenvolvimento (Local)

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar o bot
python main.py
```

### Produção (Docker)

```bash
# Construir e executar
docker build -t personal-finance-bot .
docker run -d --env-file .env personal-finance-bot
```

### Deploy no Render

1. Conecte seu repositório ao Render
2. Configure as variáveis de ambiente:
   - `TELEGRAM_BOT_TOKEN`
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_SHEET_NAME`
   - `GOOGLE_CREDENTIALS_BASE64` (base64 do arquivo JSON)
3. O deploy será automático usando `render.yaml`

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar apenas testes de parsing
python -m pytest tests/test_parsing.py -v

# Executar apenas testes de estatísticas
python -m pytest tests/test_statistics.py -v
```

## 📁 Estrutura do Projeto

```
Personal-Finance-Controller-Bot/
├── src/
│   ├── __init__.py
│   ├── bot.py                  # Bot principal
│   ├── google_sheets.py        # Gerenciador do Google Sheets
│   ├── statistics.py           # Gerador de estatísticas
│   └── webhook_server.py       # Servidor webhook para produção
├── tests/
│   ├── __init__.py
│   ├── test_parsing.py         # Testes de parsing
│   ├── test_statistics.py      # Testes de estatísticas
│   └── test_bot_unit.py        # Testes unitários do bot
├── config/                     # Credenciais (ignorado pelo git)
├── logs/                       # Logs da aplicação
├── main.py                     # Ponto de entrada
├── setup_credentials.py        # Configuração de credenciais
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Configuração Docker
├── render.yaml                 # Configuração Render
├── .env                        # Variáveis de ambiente
├── .gitignore                  # Arquivos ignorados
└── README.md                   # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.11** - Linguagem principal
- **python-telegram-bot 20.7** - API do Telegram
- **gspread 5.12.4** - Integração com Google Sheets
- **pandas 2.1.4** - Manipulação de dados
- **matplotlib/seaborn** - Geração de gráficos
- **Flask 3.0.0** - Servidor webhook
- **Docker** - Containerização
- **pytest** - Framework de testes

## 📝 Logs

Os logs são salvos em:
- Console (stdout)
- Arquivo `logs/bot.log`

## 🔒 Segurança

- Todas as credenciais são carregadas via variáveis de ambiente
- Arquivo `.env` não é versionado no Git
- Chaves privadas são tratadas de forma segura
- Validação rigorosa de entrada de dados

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `logs/bot.log`
2. Certifique-se de que todas as variáveis de ambiente estão configuradas
3. Verifique se a planilha está compartilhada com a conta de serviço
4. Execute os testes para verificar se tudo está funcionando

---
Made with ❤️ for better personal finance control
