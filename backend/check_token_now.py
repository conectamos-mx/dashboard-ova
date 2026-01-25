import os
import httpx
from dotenv import load_dotenv

# Forzar recarga
load_dotenv(override=True)

token = os.getenv('MICROSOFT_ACCESS_TOKEN', '')
print(f"Token length: {len(token)}")
print(f"Token starts with: {token[:10]}")
print(f"Has quotes at start: {token.startswith(chr(39))}")
print(f"Has quotes at end: {token.endswith(chr(39))}")
print(f"Contains dots: {'.' in token}")

headers = {'Authorization': f'Bearer {token}'}

try:
    print("\nTesting connection to Microsoft Graph (List Files)...")
    response = httpx.get('https://graph.microsoft.com/v1.0/me/drive/root/children', headers=headers, timeout=10.0)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ SUCCESS! Token is valid.")
        data = response.json()
        print(f"User: {data.get('displayName')}")
        print(f"Email: {data.get('mail') or data.get('userPrincipalName')}")
    else:
        print("❌ FAILED.")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Exception: {e}")
