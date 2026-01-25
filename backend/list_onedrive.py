import os
import httpx
from dotenv import load_dotenv

load_dotenv('backend/.env')
token = os.getenv('MICROSOFT_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

print("Listing OneDrive files...")
try:
    r = httpx.get('https://graph.microsoft.com/v1.0/me/drive/root/children', headers=headers)
    r.raise_for_status()
    items = r.json().get('value', [])
    for item in items:
        print(f"Name: {item['name']}, ID: {item['id']}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")
