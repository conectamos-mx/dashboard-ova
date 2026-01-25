import os
import httpx
from dotenv import load_dotenv

load_dotenv('backend/.env')
token = os.getenv('MICROSOFT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

def list_folder(folder_id, folder_name):
    print(f"\nListing contents of {folder_name} ({folder_id})...")
    try:
        url = f'https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children'
        r = httpx.get(url, headers=headers)
        r.raise_for_status()
        items = r.json().get('value', [])
        for item in items:
            print(f"Name: {item['name']}, ID: {item['id']}")
            if item.get('folder'):
                list_folder(item['id'], f"{folder_name}/{item['name']}")
    except Exception as e:
        print(f"Error listing {folder_name}: {e}")

# Start recursive listing from root
print("Searching for specific files...")
try:
    r = httpx.get('https://graph.microsoft.com/v1.0/me/drive/root/children', headers=headers)
    r.raise_for_status()
    items = r.json().get('value', [])
    for item in items:
        print(f"Name: {item['name']}, ID: {item['id']}")
        if item.get('folder'):
            list_folder(item['id'], item['name'])
except Exception as e:
    print(f"Error: {e}")
