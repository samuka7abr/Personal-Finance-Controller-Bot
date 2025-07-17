#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if os.getenv('RENDER') == 'true' and os.getenv('RENDER_EXTERNAL_URL'):
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