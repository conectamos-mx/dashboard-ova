"""
Script para obtener token de acceso de Microsoft Graph
Guarda el token en un archivo
"""

import os
from dotenv import load_dotenv
from msal import PublicClientApplication

load_dotenv()

CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
SCOPES = ['Files.Read', 'Files.Read.All']

# Crear aplicación pública
app = PublicClientApplication(
    CLIENT_ID,
    authority="https://login.microsoftonline.com/consumers"
)

print("=== Autenticación con Microsoft Graph ===\n")
print("Iniciando flujo de autenticación...\n")

# Iniciar Device Code Flow
flow = app.initiate_device_flow(scopes=SCOPES)

if "user_code" not in flow:
    print("❌ Error al iniciar el flujo")
    exit(1)

print(flow["message"])
print("\n⚠️  IMPORTANTE: Abre el navegador y sigue las instrucciones de arriba")
print("\nPresiona Enter cuando hayas completado la autenticación...")
input()

# Obtener el token
result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    print("\n✅ ¡Autenticación exitosa!")
    
    # Guardar token en archivo
    with open('token.txt', 'w') as f:
        f.write(result['access_token'])
    
    print(f"\n✅ Token guardado en token.txt")
    print(f"Longitud del token: {len(result['access_token'])} caracteres")
    
    # Actualizar .env
    print("\n📝 Actualizando archivo .env...")
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Buscar y reemplazar la línea del token
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('MICROSOFT_ACCESS_TOKEN='):
            lines[i] = f'MICROSOFT_ACCESS_TOKEN="{result["access_token"]}"\n'
            updated = True
            break
    
    # Si no existe, agregar al final
    if not updated:
        lines.append(f'\nMICROSOFT_ACCESS_TOKEN="{result["access_token"]}"\n')
    
    with open('.env', 'w') as f:
        f.writelines(lines)
    
    print("✅ Archivo .env actualizado")
    
else:
    print("\n❌ Error en la autenticación:")
    print(result.get("error"))
    print(result.get("error_description"))
