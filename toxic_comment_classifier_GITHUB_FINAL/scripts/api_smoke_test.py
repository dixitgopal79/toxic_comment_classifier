import json
import urllib.request

BASE = "http://127.0.0.1:8000"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=5) as r:
        return json.loads(r.read().decode())

print("Health:", json.dumps(get("/health"), indent=2))
print("Model:", json.dumps(get("/api/model"), indent=2))
