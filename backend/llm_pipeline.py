import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"


def ask_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["response"]


def answer_with_context(user_query: str, retrieved_context: str) -> str:
    full_prompt = prompt = f"""
You are a grocery price assistant.

Use ONLY the data below to answer the user's question.

Data:
{retrieved_context}

User question:
{user_query}

Instructions:
- Answer exactly what the user is asking (cheapest OR most expensive)
- Be concise (1-2 sentences)
- Clearly name the store and price
- Do NOT explain your reasoning

Answer:
"""
    return ask_ollama(full_prompt)