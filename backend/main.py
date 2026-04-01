import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from llm_pipeline import answer_with_context
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
        "to buy", "buy", "find", "the", "price", "of"
    ]

    cleaned = q
    for word in filler_words:
        cleaned = cleaned.replace(word, "")

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

    results = search_kroger_api_all_stores(search_term)
    retrieved_context = build_context_from_results(results, mode)

    if retrieved_context == "No matching products found.":
        return GroceryResponse(
            prompt=prompt.prompt,
            answer="No matching products found."
        )

    answer = answer_with_context(prompt.prompt, retrieved_context)

    return GroceryResponse(
        prompt=prompt.prompt,
        answer=answer
    )
