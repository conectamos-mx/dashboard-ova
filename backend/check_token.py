import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('MICROSOFT_ACCESS_TOKEN')
refresh_token = os.getenv('MICROSOFT_REFRESH_TOKEN')

print(f"Access Token: {'✓ Presente' if token else '✗ Falta'} ({len(token) if token else 0} caracteres)")
print(f"Refresh Token: {'✓ Presente' if refresh_token else '✗ Falta'} ({len(refresh_token) if refresh_token else 0} caracteres)")

if token:
    print(f"\nPrimeros 50 caracteres del token: {token[:50]}...")
