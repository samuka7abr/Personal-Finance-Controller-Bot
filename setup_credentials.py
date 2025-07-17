#!/usr/bin/env python3
import os
import json
import base64

def setup_google_credentials():
    credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    
    if not credentials_base64:
        print("❌ GOOGLE_CREDENTIALS_BASE64 não encontrada")
        print("Configure a variável de ambiente no Render")
        return False
    
    try:
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        
        json.loads(credentials_json)
        
        credentials_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '/app/credentials.json')
        
        credentials_dir = os.path.dirname(credentials_file)
        if credentials_dir:
            os.makedirs(credentials_dir, exist_ok=True)
        
        with open(credentials_file, 'w') as f:
            f.write(credentials_json)
        
        print(f"✅ Credenciais do Google configuradas em: {credentials_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar credenciais: {e}")
        return False

if __name__ == '__main__':
    setup_google_credentials() 