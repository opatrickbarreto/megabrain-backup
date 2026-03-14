# Google Drive OAuth Authentication Script
# Salva credenciais em ~/.gdrive-credentials.json
# para uso pelo MCP server @modelcontextprotocol/server-gdrive
import json
import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes necessarios para o Drive MCP
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
]

KEYS_FILE = r'C:\Users\Vitor\Documents\MEGABRAIN\gcp-oauth.keys.json'
CREDS_FILE = r'C:\Users\Vitor\.gdrive-credentials.json'

def main():
    creds = None

    # Se ja existe token salvo, carregar
    if os.path.exists(CREDS_FILE):
        try:
            with open(CREDS_FILE, 'r') as f:
                data = json.load(f)
            creds = Credentials(
                token=data.get('access_token'),
                refresh_token=data.get('refresh_token'),
                token_uri=data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=data.get('client_id'),
                client_secret=data.get('client_secret'),
                scopes=data.get('scopes', SCOPES),
            )
            if creds.expired and creds.refresh_token:
                print("Token expirado, renovando...")
                creds.refresh(Request())
                print("Token renovado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar token existente: {e}")
            creds = None

    # Se nao tem credenciais validas, fazer fluxo OAuth
    if not creds or not creds.valid:
        print("\n=== AUTENTICACAO GOOGLE DRIVE ===")
        print("Uma janela do navegador vai abrir para voce autorizar o acesso.")
        print("Faca login com a conta Google e clique em 'Permitir'.\n")

        flow = InstalledAppFlow.from_client_secrets_file(
            KEYS_FILE,
            scopes=SCOPES,
        )

        # Usar porta dinamica (qualquer porta disponivel)
        # Para apps instalados, Google aceita qualquer porta localhost
        creds = flow.run_local_server(
            port=0,  # 0 = porta aleatoria disponivel
            prompt='consent',
            access_type='offline',
        )
        print("\nAutorizacao concluida!")

    # Salvar no formato esperado pelo MCP server
    creds_data = {
        'access_token': creds.token,
        'refresh_token': creds.refresh_token,
        'scope': ' '.join(creds.scopes) if creds.scopes else '',
        'token_type': 'Bearer',
        'expiry_date': int(creds.expiry.timestamp() * 1000) if creds.expiry else 0,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'token_uri': creds.token_uri,
    }

    os.makedirs(os.path.dirname(CREDS_FILE), exist_ok=True)
    with open(CREDS_FILE, 'w') as f:
        json.dump(creds_data, f, indent=2)

    print(f"\nCredenciais salvas em: {CREDS_FILE}")
    print("\nAgora reinicie o Claude Code para o MCP do Google Drive funcionar.")

if __name__ == '__main__':
    main()
