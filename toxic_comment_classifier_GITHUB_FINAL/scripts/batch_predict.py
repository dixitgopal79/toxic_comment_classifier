import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8000/api/predict/batch"

texts = sys.argv[1:] or [
    "This is a normal comment.",
    "I disagree with your opinion.",
]

payload = json.dumps({"texts": texts}).encode()
request = urllib.request.Request(
    BASE,
    data=payload,
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(request, timeout=30) as response:
    print(response.read().decode())
