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
    full_prompt = f"""
    You are a grocery price assistant.

    Use ONLY the data below.

    Data:
    {retrieved_context}

    User question:
    {user_query}

    Rules:
    - Return exactly ONE result only.
    - Do NOT list multiple options.
    - Do NOT repeat the input data.
    - Do NOT explain reasoning.
    - Output exactly in this format and nothing else:

    Store: <store name> | Item: <item name> | Price: <price>

    Answer:
    """
    return ask_ollama(full_prompt).strip()