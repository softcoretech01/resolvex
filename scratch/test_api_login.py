import urllib.request
import json

def test_login(email, password, label=""):
    url = "http://127.0.0.1:8000/api/login"
    data = {"user_name": email, "password": password}
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"[OK] [{label}] Login SUCCESS: user_name={result.get('user_name')}, role={result.get('role')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"[FAIL] [{label}] HTTP {e.code}: {body}")
    except Exception as e:
        print(f"[ERROR] [{label}]: {e}")

if __name__ == "__main__":
    test_login("sachin532210@gmail.com", "admin123", "Sachin")
