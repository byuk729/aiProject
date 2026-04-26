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
from backend.search.search_router import search

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
    return item["promo_price"] if item["promo_price"] else item["price"]

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
        "where can i buy", "where do i buy", "where do i get",
        "where", "what", "how", "place",
        "is", "are", "do", "does", "did",
        "to buy", "buy", "get", "find",
        "the", "price", "of", "and",
        "i need", "i want", "i", "me",
        "near uva", "near me", "in charlottesville",
        "budget around", "budget of", "with a budget", "budget",
        "with", "near", "please", "around", "a", "an"
    ]

    cleaned = q
    # remove dollar amounts first
    cleaned = re.sub(r'\$\d+', '', cleaned)
    cleaned = re.sub(r'\d+ dollars', '', cleaned)

    # strip whole words only using word boundaries
    for phrase in filler_words:
        cleaned = re.sub(rf'\b{re.escape(phrase)}\b', ' ', cleaned)

    search_term = " ".join(cleaned.split()).strip()

    words = search_term.split()
    words = [w for w in words if len(w) > 2]
    search_term = " ".join(words)

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
            f"Store: {item['store_name']} | Item: {item['product_name']} | Price: {price}"
        )

    return "\n".join(lines)

@app.post('/api/grocery-recs', response_model=GroceryResponse)
def create_grocery_recs(prompt: Prompt) -> GroceryResponse:
    parsed = parse_query(prompt.prompt)
    search_term = parsed["search_term"]
    mode = parsed["mode"]

    print(f"DEBUG search_term: '{search_term}'")

    results = search("Charlottesville", search_term, k=30)
    
    results = [r for r in results if "egg" in r["product_name"].lower()]

    if not results:
        return GroceryResponse(
            prompt=prompt.prompt,
            answer="No matching products found."
        )

    if mode == "most_expensive":
        top_results = sorted(results, key=get_effective_price, reverse=True)[:3]
    else:
        top_results = sorted(results, key=get_effective_price)[:3]

    lines = []

    for item in top_results:
        price = get_effective_price(item)
        lines.append(
            f"{item['store_name']} | {item['product_name']} | ${price}"
        )

    retrieved_context = "\n".join(lines)
    answer = answer_with_context(prompt.prompt, retrieved_context)

    return GroceryResponse(
        prompt=prompt.prompt,
        answer=answer
    )
