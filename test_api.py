
import urllib.request
import json
import socket

def test_config():
    from config import DOC_NAME, PG_CONN_STR
    print(f"Config DOC_NAME: {DOC_NAME}")
    print(f"Config PG_CONN_STR: {PG_CONN_STR}")

def call_api(endpoint):
    url = f"http://127.0.0.1:8000{endpoint}"
    print(f"Calling {url}...")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            data = json.loads(response.read().decode())
            print(f"  Status: {status}")
            print(f"  Data: {data}")
    except Exception as e:
        print(f"  Error calling {url}: {e}")

if __name__ == "__main__":
    test_config()
    call_api("/health")
    call_api("/chapters")
