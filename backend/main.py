import os
import sys
import re
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from backend.llm_pipeline import answer_with_context
from scripts.search import search_kroger_api_all_stores

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

class GroceryResponse(BaseModel):
    prompt: str
    answer: str
    
# helper
def get_effective_price(item):
    return item["price_promo"] if item["price_promo"] else item["price_regular"]

# helper
def parse_query(user_query: str) -> dict:
    q = user_query.lower().replace("?", "").strip()

    cheapest_words = [
        "cheap", "cheapest", "lowest", "lowest price",
        "least expensive", "affordable", "best deal"
    ]
    expensive_words = [
        "expensive", "most expensive", "highest", "highest price",
        "priciest", "costliest"
    ]

    mode = "cheapest" # default

    if any(word in q for word in expensive_words):
        mode = "most_expensive"
    elif any(word in q for word in cheapest_words):
        mode = "cheapest"

    filler_words = cheapest_words + expensive_words + [
    "what is", "whats", "where is", "where can i get",
    "to buy", "buy", "find", "the", "price", "of", "and",
    "i need", "i want", "near uva", "near me", "in charlottesville",
    "budget around", "budget of", "with a budget", "budget",
    "with", "near", "please", "around", "a"
]

    cleaned = q
    # remove dollar amounts first
    cleaned = re.sub(r'\$\d+', '', cleaned)
    cleaned = re.sub(r'\d+ dollars', '', cleaned)

    # strip whole words only using word boundaries
    for phrase in filler_words:
        cleaned = re.sub(rf'\b{re.escape(phrase)}\b', ' ', cleaned)

    search_term = " ".join(cleaned.split()).strip()

    return {
        "search_term": search_term,
        "mode": mode
    }

@app.get('/')
def root():
    return {"Hello": "World"}

def build_context_from_results(results, mode):
    if not results:
        return "No matching products found."
    
    lines = []

    if mode == "most_expensive":
        results = sorted(results, key=get_effective_price, reverse=True)[:1]
    else:
        results = sorted(results, key=get_effective_price)[:1]

    for item in results:
        price = get_effective_price(item)
        lines.append(
            f"Store: {item['store_name']} | Item: {item['item_name']} | Price: {price}"
        )

    return "\n".join(lines)

@app.post('/api/grocery-recs', response_model=GroceryResponse)
def create_grocery_recs(prompt: Prompt) -> GroceryResponse:
    parsed = parse_query(prompt.prompt)
    search_term = parsed["search_term"]
    mode = parsed["mode"]

    print(f"DEBUG search_term: '{search_term}'")

    # keep modifiers attached to the next word
    raw_words = search_term.split()
    items = []
    i = 0
    while i < len(raw_words):
        modifiers = ["organic", "fresh", "whole", "low", "fat", "reduced", "non", "free"]
        if raw_words[i] in modifiers and i + 1 < len(raw_words):
            items.append(f"{raw_words[i]} {raw_words[i+1]}")
            i += 2
        else:
            items.append(raw_words[i])
            i += 1

    print(f"DEBUG items: {items}")
    all_lines = []

    results = search_kroger_api_all_stores(search_term)
    retrieved_context = build_context_from_results(results, mode)

    for item in items:
        results = search_kroger_api_all_stores(item)
        if results:
            if mode == "most_expensive":
                best = sorted(results, key=get_effective_price, reverse=True)[0]
            else:
                best = sorted(results, key=get_effective_price)[0]
            
            price = get_effective_price(best)
            all_lines.append(
                f"Store: {best['store_name']} | Item: {best['item_name']} | Price: ${price}"
            )

    if not all_lines:
        return GroceryResponse(
            prompt=prompt.prompt,
            answer="No matching products found."
        )
    
    retrieved_context = "\n".join(all_lines)
    answer = answer_with_context(prompt.prompt, retrieved_context)

    return GroceryResponse(
        prompt=prompt.prompt,
        answer=answer
    )
