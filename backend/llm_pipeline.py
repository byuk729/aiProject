import requests
import re 
import json
from grocery_api import model, product_vecs, catalog, product_to_text
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

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

def normalize_price(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    match = re.search(r"(\d+(\.\d+)?)", str(value))
    if match:
        return float(match.group(1))

    return None

def extract_price(text: str):
    match = re.search(r"(under|less than|below)\s*\$?(\d+(\.\d+)?)", text.lower())
    return float(match.group(2)) if match else None


def detect_snap(text: str):
    return bool(re.search(r"\b(snap|ebt)\b", text.lower()))


def detect_sale(text: str):
    return bool(re.search(r"\b(on sale|deal|discount)\b", text.lower()))


def extract_brand(text: str):
    known_brands = ["kroger", "walmart", "target", "costco"]

    for brand in known_brands:
        if brand in text.lower():
            return brand.capitalize()
    return None


def extract_keywords(text: str):
    stopwords = {
        "i","need","want","something","for","the","a","an",
        "under","less","than","below","on","sale","deal",
        "discount","snap","ebt","eligible","cheap","best",
        "and","or","with","some","get","find","me","my",
        "stuff","things","thing","food","item","items",
        "night","day","good","great","any","please","just",
        "random","words","blah","healthy","dollars","dollar",
        "uva","near","at","around","store","stores","where",
        "can","buy","cheapest","lowest","how","much","does",
        "cost","price","is","are","do","to","in","of","from",
        "have","has","had","got","looking","give","show","tell",
        "what","which","when","will","would","could","should",
        "was","were","be","been","being","not","no","yes",
        "nead","also","too","very","really","just","only",
        "their","they","them","there","here","this","that",
        "these","those","we","us","our","you","your","it","its",
    }

    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    keywords = [w for w in words if w not in stopwords]

    return keywords if keywords else words

def detect_cheapest(text: str) -> bool:
    return bool(re.search(r"\b(cheapest|lowest price|best price|best deal|most affordable)\b", text.lower()))

def safe_json_extract(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None
    return None

def normalize_price(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    match = re.search(r"(\d+(\.\d+)?)", str(value))
    if match:
        return float(match.group(1))

    return None

def parse_user_query(user_input: str) -> dict:
    text = user_input.strip()

    # -------------------------------
    # RULE-BASED FIRST
    # -------------------------------
    parsed = {
        "keywords": extract_keywords(text),
        "max_price": extract_price(text),
        "snap_only": detect_snap(text),
        "on_sale": detect_sale(text),
        "brand": extract_brand(text),
        "cheapest": detect_cheapest(text)
    }

    # -------------------------------
    # DECIDE IF LLM NEEDED
    # -------------------------------
    needs_llm = len(parsed["keywords"]) == 0

    if needs_llm:
        prompt = f"""
You are a grocery search parser.

Extract ONLY explicit info.

Rules:
- keywords must be real food items (no "product")
- on_sale ONLY if "on sale", "deal", "discount"
- max_price ONLY from "under $X", "less than $X", "below $X"
- snap_only if SNAP or EBT
- brand only if explicitly mentioned

Return JSON only:
{{"keywords": [], "max_price": null, "snap_only": false, "on_sale": false, "brand": null}}

User: "{user_input}"
"""

        raw = ask_ollama(prompt)
        llm_data = safe_json_extract(raw)

        if llm_data:
            # merge (RULES WIN)
            for key in parsed:
                if parsed[key] is None or parsed[key] == []:
                    parsed[key] = llm_data.get(key, parsed[key])
                    
    # -------------------------------
    # FINAL FIXES / GUARDRAILS
    # -------------------------------

    # Fix "product" bug
    if parsed["keywords"] == ["product"]:
        parsed["keywords"] = extract_keywords(text)

    if not parsed["keywords"]:
        parsed["keywords"] = extract_keywords(text)
    # Force types
    # Safe type normalization
    parsed["max_price"] = normalize_price(parsed["max_price"])
    parsed["snap_only"] = bool(parsed["snap_only"])
    parsed["on_sale"] = bool(parsed["on_sale"])
    # Remove brand from keywords
    if parsed["brand"]:
        parsed["keywords"] = [
            k for k in parsed["keywords"]
            if k.lower() != parsed["brand"].lower()
        ]
    return {
        "keywords": parsed["keywords"],
        "max_price": parsed["max_price"],
        "snap_only": parsed["snap_only"],
        "on_sale": parsed["on_sale"],
        "brand": parsed["brand"],
    }

def semantic_search(user_input: str, top_k: int = 3) -> str:
    parsed = parse_user_query(user_input)
    print(f"[Parser] {parsed}")

    keywords = parsed["keywords"] if parsed["keywords"] else [user_input]
    find_cheapest = parsed.get("find_cheapest", False)

    final_results = []

    for keyword in keywords:
        query_vec = model.encode([keyword], convert_to_numpy=True)
        scores = cosine_similarity(query_vec, product_vecs)[0]
        top_indices = np.argsort(scores)[::-1]

        keyword_results = []
        seen = set()

        for i in top_indices:
            row = catalog.iloc[i]

            if parsed["max_price"] is not None and row.price_regular > parsed["max_price"]:
                continue
            if parsed["snap_only"] and not row.snap_eligible:
                continue
            if parsed["on_sale"]:
                if pd.isna(row.price_promo) or row.price_promo >= row.price_regular:
                    continue
            if parsed["brand"] and parsed["brand"].lower() not in str(row.brand).lower():
                continue

            text = product_to_text(row)
            if text in seen:
                continue
            seen.add(text)

            keyword_results.append((row.price_regular, scores[i], text))

            if len(keyword_results) >= 3:
                break

        if keyword_results:
            if find_cheapest:
                keyword_results.sort(key=lambda x: x[0])
            else:
                keyword_results.sort(key=lambda x: x[1], reverse=True)

            print(f"[Candidates for '{keyword}']")
            for price, score, text in keyword_results:
                print(f"  ${price:.2f} | score={score:.3f} | {text[:80]}")

            final_results.append(keyword_results[0][2])

    return "\n".join(final_results) if final_results else "No matching products found."

def answer_with_context(user_query: str, retrieved_context: str) -> str:
    first_result = retrieved_context.split("\n")[0]

    full_prompt = f"""You are a grocery assistant. Use ONLY the data below. Do NOT change any numbers.

Data: {first_result}

Reply in this exact format:
Store: <store name> | Item: <item name> | Price: <copy price exactly from data>

Answer:"""

    try:
        return ask_ollama(full_prompt).strip()
    except Exception as e:
        print(f"[Ollama error] {e}")
        return first_result