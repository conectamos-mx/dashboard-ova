import msal
import os
import time
from dotenv import load_dotenv

# Cargar configuración
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)

CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
TENANT_ID = os.getenv('MICROSOFT_TENANT_ID', 'consumers')

# Scopes necesarios para Graph API y Refresh Token
# Usamos URLs completas de Graph para asegurar un token v2.0 (JWT)
SCOPES = [
    'https://graph.microsoft.com/Files.Read.All',
    'https://graph.microsoft.com/User.Read'
]

def authenticate():
    print("============================================================")
    print("🔐 AUTENTICACIÓN ROBUSTA CON MSAL (MICROSOFT GRAPH)")
    print("============================================================")
    
    # Configurar el caché persistente (igual que en graph_client.py)
    CACHE_PATH = os.path.join(os.path.dirname(__file__), 'token_cache.bin')
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache.deserialize(f.read())

    # Configurar la aplicación MSAL
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.PublicClientApplication(
        CLIENT_ID, 
        authority=authority,
        token_cache=cache
    )
    
    # Iniciar flujo de código de dispositivo
    flow = app.initiate_device_flow(scopes=SCOPES)
    
    if "user_code" not in flow:
        print(f"❌ Error al iniciar flujo: {flow.get('error_description', 'Error desconocido')}")
        return

    print("\n" + "="*60)
    print("📋 INSTRUCCIONES:")
    print("="*60)
    print(f"\n1. Abre esta URL: {flow['verification_uri']}")
    print(f"2. Ingresa este código: {flow['user_code']}")
    print("\n⏳ Esperando autenticación...")

    # Esperar el token
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        access_token = result['access_token']
        refresh_token = result.get('refresh_token', '')
        
        # Validar si es JWT (debe tener puntos)
        has_dots = "." in access_token
        
        print("\n✅ ¡Autenticación exitosa!")
        print(f"Format: {'JWT (Correcto)' if has_dots else 'Opaco (Inválido para Graph)'}")
        
        # Guardar el caché actualizado
        with open(CACHE_PATH, "w") as f:
            f.write(cache.serialize())
        
        # Guardar en .env (opcional, por compatibilidad)
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, 'r') as f:
                lines = f.readlines()
                
            new_lines = []
            found_access = False
            found_refresh = False
            
            for line in lines:
                if line.startswith('MICROSOFT_ACCESS_TOKEN='):
                    new_lines.append(f"MICROSOFT_ACCESS_TOKEN={access_token}\n")
                    found_access = True
                elif line.startswith('MICROSOFT_REFRESH_TOKEN='):
                    new_lines.append(f"MICROSOFT_REFRESH_TOKEN={refresh_token}\n")
                    found_refresh = True
                else:
                    new_lines.append(line)
            
            if not found_access:
                new_lines.append(f"MICROSOFT_ACCESS_TOKEN={access_token}\n")
            if not found_refresh:
                new_lines.append(f"MICROSOFT_REFRESH_TOKEN={refresh_token}\n")
                
            with open(ENV_PATH, 'w') as f:
                f.writelines(new_lines)
        
        print("\n💾 Tokens actualizados en .env")
        if not has_dots:
            print("⚠️ AVISO: El token sigue siendo opaco. Intentaremos usarlo de todas formas.")
    else:
        print(f"\n❌ Error: {result.get('error')}")
        print(f"Descripción: {result.get('error_description')}")

if __name__ == "__main__":
    authenticate()
