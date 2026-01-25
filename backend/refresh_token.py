"""
Script para refrescar el Access Token de Microsoft Graph API
"""
import os
import httpx
from dotenv import load_dotenv, set_key

load_dotenv()

CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
TENANT_ID = os.getenv('MICROSOFT_TENANT_ID', 'common')
REFRESH_TOKEN = os.getenv('MICROSOFT_REFRESH_TOKEN')

if not REFRESH_TOKEN:
    print("❌ Error: No se encontró MICROSOFT_REFRESH_TOKEN en .env")
    print("Ejecuta: python setup_onedrive.py para autenticarse por primera vez")
    exit(1)

if not CLIENT_ID:
    print("❌ Error: Falta MICROSOFT_CLIENT_ID en .env")
    exit(1)

print("🔄 Refrescando Access Token...")

token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# Configurar datos para la solicitud
data = {
    'client_id': CLIENT_ID,
    'refresh_token': REFRESH_TOKEN,
    'grant_type': 'refresh_token',
    'scope': 'Files.Read Files.Read.All User.Read offline_access'
}

# Incluir client_secret solo si existe (para clientes confidenciales)
if CLIENT_SECRET:
    data['client_secret'] = CLIENT_SECRET

try:
    response = httpx.post(token_url, data=data)
    response.raise_for_status()
    
    tokens = response.json()
    new_access_token = tokens['access_token']
    new_refresh_token = tokens.get('refresh_token', REFRESH_TOKEN)
    
    # Validar formato del token nuevo (opcional, solo informativo)
    if '.' not in new_access_token:
        print("⚠️  Info: El nuevo token tampoco tiene formato JWT estándar (posiblemente opaco)")
    
    # Actualizar .env
    env_file = '.env'
    set_key(env_file, 'MICROSOFT_ACCESS_TOKEN', new_access_token, quote_mode="never")
    set_key(env_file, 'MICROSOFT_REFRESH_TOKEN', new_refresh_token, quote_mode="never")
    
    print("✅ Access Token actualizado exitosamente")
    if new_refresh_token != REFRESH_TOKEN:
        print("✅ Refresh Token actualizado")
    
    print(f"⏰ Nuevo token válido por {tokens.get('expires_in', 3600)} segundos")
    
except httpx.HTTPStatusError as e:
    print(f"❌ Error HTTP: {e.response.status_code}")
    print(f"Respuesta: {e.response.text}")
    print("El refresh token podría estar expirado o revocado. Ejecuta setup_onedrive.py")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
