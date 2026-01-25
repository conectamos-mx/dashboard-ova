import os
import httpx
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('MICROSOFT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

print("=== Probando acceso a OneDrive ===\n")

# Probar /me/drive
print("1. Probando /me/drive...")
try:
    response = httpx.get('https://graph.microsoft.com/v1.0/me/drive', headers=headers, timeout=30.0)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Drive ID: {data.get('id')}")
        print(f"   Owner: {data.get('owner', {}).get('user', {}).get('displayName')}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Probar acceso al archivo
print("\n2. Probando acceso al archivo de ventas...")
file_id = os.getenv('EXCEL_VENTAS_ITEM_ID')
url = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}'

try:
    response = httpx.get(url, headers=headers, timeout=30.0)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Archivo: {data.get('name')}")
        print(f"   Tamaño: {data.get('size')} bytes")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Probar descarga
print("\n3. Probando descarga del archivo...")
download_url = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'

try:
    response = httpx.get(download_url, headers=headers, timeout=60.0, follow_redirects=True)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Descarga exitosa: {len(response.content)} bytes")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")
