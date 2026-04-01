import requests

url = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "qwen2.5:0.5b",
    "prompt": "Say hello in one sentence.",
    "stream": False
}

response = requests.post(url, json=payload)

print(response.json()["response"])