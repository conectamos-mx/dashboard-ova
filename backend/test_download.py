import os
import httpx
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('MICROSOFT_ACCESS_TOKEN')
item_id = os.getenv('EXCEL_VENTAS_ITEM_ID')

print(f"🔍 Probando descarga con follow_redirects=True...")

headers = {
    'Authorization': f'Bearer {token}'
}

download_url = f'https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/content'

try:
    print(f"\n📥 Descargando desde: {download_url}")
    response = httpx.get(download_url, headers=headers, timeout=60.0, follow_redirects=True)
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"✅ Descarga exitosa!")
        print(f"Tamaño: {len(response.content)} bytes")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
    else:
        print(f"❌ Error {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        
    response.raise_for_status()
    
except httpx.HTTPStatusError as e:
    print(f"\n❌ HTTPStatusError:")
    print(f"   Status: {e.response.status_code}")
    print(f"   URL: {e.request.url}")
    print(f"   Response: {e.response.text[:500]}")
except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}: {e}")
