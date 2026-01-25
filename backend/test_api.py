import sys
sys.path.insert(0, 'c:/Users/Jose/Desktop/Dashboard OVA/backend')

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

try:
    response = client.get("/api/summary")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
