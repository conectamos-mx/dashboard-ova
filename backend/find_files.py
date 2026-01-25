import os
import httpx
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('MICROSOFT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

print("=== Buscando archivos Excel en OneDrive ===\n")

# Listar archivos en la raíz
print("Buscando archivos .xlsx...\n")
url = 'https://graph.microsoft.com/v1.0/me/drive/root/search(q=\'.xlsx\')'

try:
    response = httpx.get(url, headers=headers, timeout=30.0)
    if response.status_code == 200:
        data = response.json()
        files = data.get('value', [])
        
        print(f"Encontrados {len(files)} archivos Excel\n")
        
        ventas_file = None
        almacen_file = None
        
        for file in files:
            name = file.get('name', '')
            file_id = file.get('id', '')
            size = file.get('size', 0)
            
            print(f"📄 {name}")
            print(f"   ID: {file_id}")
            print(f"   Tamaño: {size:,} bytes")
            print()
            
            if 'VENTAS' in name.upper():
                ventas_file = file_id
            if 'ALMACÉN' in name.upper() or 'ALMACEN' in name.upper():
                almacen_file = file_id
        
        print("\n" + "="*60)
        print("IDs para configurar en .env:")
        print("="*60)
        if ventas_file:
            print(f"\nEXCEL_VENTAS_ITEM_ID={ventas_file}")
        if almacen_file:
            print(f"EXCEL_ALMACEN_ITEM_ID={almacen_file}")
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
