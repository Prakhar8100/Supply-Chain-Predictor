import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

models_to_test = [
    "google/gemma-2-9b-it",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta"
]

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}
data = {
    "inputs": "Hello",
    "parameters": {"max_new_tokens": 10}
}

for model in models_to_test:
    url = f"https://api-inference.huggingface.co/models/{model}"
    print(f"Testing {model}...")
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Success! Response: {response.json()}")
        else:
            print(f"Error: {response.text[:100]}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 40)
