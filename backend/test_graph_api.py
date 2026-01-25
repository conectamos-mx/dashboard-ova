import os
import httpx
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('MICROSOFT_ACCESS_TOKEN')
item_id = os.getenv('EXCEL_VENTAS_ITEM_ID')

print(f"🔍 Probando acceso a Microsoft Graph API...")
print(f"Item ID: {item_id}")

headers = {
    'Authorization': f'Bearer {token}'
}

# Probar primero obtener info del usuario
print("\n1️⃣ Probando /me...")
try:
    response = httpx.get('https://graph.microsoft.com/v1.0/me', headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Usuario: {data.get('userPrincipalName', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {e}")

# Probar obtener info del drive
print("\n2️⃣ Probando /me/drive...")
try:
    response = httpx.get('https://graph.microsoft.com/v1.0/me/drive', headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Drive ID: {data.get('id', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {e}")

# Probar acceder al archivo
print(f"\n3️⃣ Probando /me/drive/items/{item_id}...")
try:
    response = httpx.get(f'https://graph.microsoft.com/v1.0/me/drive/items/{item_id}', headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Archivo: {data.get('name', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {e}")

# Probar descargar el archivo
print(f"\n4️⃣ Probando /me/drive/items/{item_id}/content...")
try:
    response = httpx.get(f'https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/content', headers=headers, timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Descarga exitosa! Tamaño: {len(response.content)} bytes")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   Exception: {e}")
