"""
Script para autenticarse con Microsoft Graph API usando Device Code Flow
Este método no requiere configurar redirect URIs
"""
import os
import httpx
import time
from dotenv import load_dotenv, set_key

load_dotenv()

CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
TENANT_ID = os.getenv('MICROSOFT_TENANT_ID', 'consumers')

if not CLIENT_ID:
    print("❌ Error: Falta CLIENT_ID en .env")
    exit(1)

print("=" * 60)
print("🔐 AUTENTICACIÓN CON MICROSOFT GRAPH API")
print("=" * 60)
print("\n📱 Usando Device Code Flow (sin redirect URI)\n")

# Paso 1: Solicitar código de dispositivo
device_code_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"

data = {
    'client_id': CLIENT_ID,
    # Scopes simplificados para cuentas personales (MSA)
    'scope': 'Files.Read.All User.Read offline_access'
}

try:
    print("🔄 Solicitando código de dispositivo...")
    response = httpx.post(device_code_url, data=data, timeout=30)
    response.raise_for_status()
    
    device_code_data = response.json()
    
    user_code = device_code_data['user_code']
    device_code = device_code_data['device_code']
    verification_uri = device_code_data['verification_uri']
    expires_in = device_code_data['expires_in']
    interval = device_code_data.get('interval', 5)
    
    print("\n" + "=" * 60)
    print("📋 INSTRUCCIONES:")
    print("=" * 60)
    print(f"\n1. Abre esta URL en tu navegador:")
    print(f"   👉 {verification_uri}")
    print(f"\n2. Ingresa este código:")
    print(f"   👉 {user_code}")
    print(f"\n3. Inicia sesión con tu cuenta de Microsoft")
    print(f"\n⏰ Tienes {expires_in // 60} minutos para completar este proceso")
    print("\n⏳ Esperando autenticación...")
    
    # Paso 2: Polling para obtener tokens
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    token_data = {
        'client_id': CLIENT_ID,
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code
    }
    
    max_attempts = expires_in // interval
    
    for attempt in range(max_attempts):
        time.sleep(interval)
        
        try:
            token_response = httpx.post(token_url, data=token_data, timeout=30)
            
            if token_response.status_code == 200:
                # ¡Éxito!
                tokens = token_response.json()
                access_token = tokens['access_token']
                refresh_token = tokens['refresh_token']
                expires_in_token = tokens.get('expires_in', 3600)
                
                print(f"\n✅ ¡Autenticación exitosa!")
                print(f"⏰ Access token válido por {expires_in_token} segundos (~{expires_in_token//60} minutos)")

                # Validar formato del token
                if '.' not in access_token:
                    print("\n⚠️  ADVERTENCIA: El token recibido NO parece ser un JWT válido (no contiene puntos)")
                else:
                    print(f"ℹ️  Token validado: contiene {access_token.count('.')} puntos")
                
                # Guardar en .env
                env_file = '.env'
                # set_key a veces agrega comillas innecesarias que pueden confundir si el token tiene caracteres especiales
                # Vamos a intentar guardar sin comillas forzadas si set_key lo permite, o confiar en set_key
                set_key(env_file, 'MICROSOFT_ACCESS_TOKEN', access_token, quote_mode="never")
                set_key(env_file, 'MICROSOFT_REFRESH_TOKEN', refresh_token, quote_mode="never")
                
                print(f"\n💾 Tokens guardados en {env_file}")
                print("\n✅ ¡Configuración completada!")
                print("🚀 El dashboard ya puede acceder a OneDrive")
                exit(0)
                
            elif token_response.status_code == 400:
                error_data = token_response.json()
                error_code = error_data.get('error', '')
                
                if error_code == 'authorization_pending':
                    # Usuario aún no ha completado la autenticación
                    print(f"⏳ Esperando... ({attempt + 1}/{max_attempts})")
                    continue
                elif error_code == 'authorization_declined':
                    print("\n❌ Autenticación rechazada por el usuario")
                    exit(1)
                elif error_code == 'expired_token':
                    print("\n❌ El código expiró. Ejecuta el script de nuevo.")
                    exit(1)
                else:
                    print(f"\n❌ Error: {error_code}")
                    print(f"Descripción: {error_data.get('error_description', 'N/A')}")
                    exit(1)
            else:
                print(f"\n❌ Error HTTP: {token_response.status_code}")
                print(f"Respuesta: {token_response.text}")
                exit(1)
                
        except Exception as e:
            print(f"\n❌ Error en polling: {e}")
            exit(1)
    
    print("\n❌ Tiempo de espera agotado. Ejecuta el script de nuevo.")
    exit(1)
    
except httpx.HTTPStatusError as e:
    print(f"❌ Error HTTP: {e.response.status_code}")
    print(f"Respuesta: {e.response.text}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
