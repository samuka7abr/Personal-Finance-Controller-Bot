#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if os.getenv('RENDER') == 'true' and os.getenv('RENDER_EXTERNAL_URL'):
    # Verificar se já existe arquivo de credenciais (arquivo secreto do Render)
    credentials_file = '/app/credentials.json'
    if os.path.exists(credentials_file):
        print(f"✅ Usando arquivo secreto de credenciais: {credentials_file}")
    else:
        # Fallback para base64 se arquivo secreto não existir
        print("📦 Arquivo secreto não encontrado, tentando usar GOOGLE_CREDENTIALS_BASE64...")
        from setup_credentials import setup_google_credentials
        if not setup_google_credentials():
            print("❌ Falha ao configurar credenciais. Abortando...")
            sys.exit(1)

if __name__ == '__main__':
    if os.getenv('RENDER') == 'true' and os.getenv('RENDER_EXTERNAL_URL'):
        print("🌐 Iniciando em modo WEBHOOK para produção...")
        from src.webhook_server import main
        main()
    else:
        print("🔄 Iniciando em modo POLLING para desenvolvimento...")
        from src.bot import main
        main() 