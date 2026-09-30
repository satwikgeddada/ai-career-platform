import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "gemini-3.7-flash",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}]
}
resp = requests.post("https://codecraftapi.com/v1/chat/completions", headers=headers, json=data, timeout=30)
print(f"Status: {resp.status_code}")
result = resp.json()
if "choices" in result:
    print("SUCCESS:", result["choices"][0]["message"]["content"])
else:
    print("Response:", result)
