import os
import re
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="Cville Grocery Recommender")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = os.path.join(os.path.dirname(__file__), "../data/clean")
products = pd.read_csv(os.path.join(BASE, "kroger_products.csv"))
stores = pd.read_csv(os.path.join(BASE, "stores.csv"))
catalog = products.merge(stores, on="store_id", how="left")


model = SentenceTransformer("all-MiniLM-L6-v2")

def store_to_text(sid: int) -> str:
    s = stores[stores.store_id == sid].iloc[0]
    p = products[products.store_id == sid]
    return (
        f"{s.store_name} at {s.address}, {s.city} {s.state}. "
        f"Categories: {', '.join(p.category.unique())}. "
        f"Items: {', '.join(p.item_name.tolist()[:30])}. "
        f"Brands: {', '.join(p.brand.dropna().unique()[:8])}. "
        f"Price range ${p.price_regular.min():.2f}–${p.price_regular.max():.2f}, "
        f"avg ${p.price_regular.mean():.2f}. "
        f"SNAP-eligible products: {int(p.snap_eligible.sum())}."
    )

store_ids = stores.store_id.tolist()
store_texts = [store_to_text(sid) for sid in store_ids]
store_vecs = model.encode(store_texts, convert_to_numpy=True)

print(f"[ready] {len(store_ids)} stores indexed.")

# intent parsing

GROCERY_ITEMS = [
    "whole milk", "2% milk", "organic milk", "skim milk", "milk",
    "light bulbs", "light bulb", "bulbs", "bulb",
    "apples", "apple",
    "eggs", "bread", "butter", "cheese", "yogurt",
    "juice", "water", "chicken", "beef", "pork",
    "pasta", "rice", "beans", "cereal",
]

PREFERENCES = {
    "organic": ["organic", "natural"],
    "snap": ["snap", "ebt", "food stamp"],
    "cheap": ["cheap", "affordable", "inexpensive", "low cost", "budget friendly"],
    "sale": ["sale", "on sale", "discount", "deal", "promo"],
    "bulk": ["bulk", "family size", "large"],
}

LOCATIONS = [
    "barracks road", "barracks",
    "rio hill", "rio",
    "hollymead",
    "blue ridge",
    "emmet",
]

def parse(prompt: str) -> dict:
    t = prompt.lower()

    # budget + only grabs if there are dollar signs or some key words
    budget = None
    m = re.search(
        r"(?:(?:under|below|less than|budget[:\s]*|up to|max[:\s]*)\s*\$?\s*(\d+(?:\.\d+)?)"
        r"|\$\s*(\d+(?:\.\d+)?))",
        t
    )
    if m:
        budget = float(m.group(1) or m.group(2))

    items = []
    for item in GROCERY_ITEMS:
        if item in t and not any(item in existing for existing in items):
            items.append(item)

    prefs = [p for p, kws in PREFERENCES.items() if any(kw in t for kw in kws)]

    location = next((loc.title() for loc in LOCATIONS if loc in t), None)

    return {
        "items": items,
        "budget": budget,
        "location": location,
        "prefs": prefs,
    }

def intent_to_query(raw: str, intent: dict) -> str:
    """Build a rich query string that gets embedded for similarity search."""
    parts = [raw]
    if intent["items"]:
        parts.append("Items needed: " + ", ".join(intent["items"]))
    if intent["prefs"]:
        parts.append("Preferences: " + ", ".join(intent["prefs"]))
    if intent["budget"]:
        parts.append(f"Budget: ${intent['budget']:.0f}")
    if intent["location"]:
        parts.append(f"Near: {intent['location']}")
    return ". ".join(parts)

# product matching

def match_products(sid: int, intent: dict, top_n: int = 5) -> list[dict]:
    rows = catalog[catalog.store_id == sid].copy()

    if intent["budget"]:
        rows = rows[rows.price_regular <= intent["budget"]]
    if "snap" in intent["prefs"]:
        filtered = rows[rows.snap_eligible == True]
        if not filtered.empty:
            rows = filtered
    if "sale" in intent["prefs"]:
        filtered = rows[rows.price_promo.notna()]
        if not filtered.empty:
            rows = filtered

    wanted = [i.lower() for i in intent["items"]]
    prefer_organic = "organic" in intent["prefs"]

    def score(name: str) -> int:
        n = name.lower()
        base = sum(1 for w in wanted if w in n or any(part in n for part in w.split()))
        org_bonus = 2 if prefer_organic and "organic" in n else 0
        return base + org_bonus

    rows["_score"] = rows.item_name.apply(score)
    rows = rows.sort_values(["_score", "price_regular"], ascending=[False, True])

    seen = set()
    out = []
    for _, r in rows.iterrows():
        name_key = r.item_name.strip().lower()
        if name_key in seen:
            continue
        seen.add(name_key)
        on_sale = pd.notna(r.price_promo)
        out.append({
            "name": r.item_name,
            "brand": r.brand if pd.notna(r.brand) else "Unknown",
            "category": r.category,
            "price": float(r.price_promo if on_sale else r.price_regular),
            "regular_price": float(r.price_regular),
            "on_sale": on_sale,
            "snap": bool(r.snap_eligible),
        })
        if len(out) >= top_n:
            break
    return out

# explanation
def explain(store_name: str, intent: dict, matched: list[dict], score: float, rank: int) -> str:
    openers = ["Top pick", "Runner-up", "Also worth checking"]
    opener = openers[min(rank, 2)]

    budget = intent["budget"]
    prefs = intent["prefs"]
    location = intent["location"]

    affordable = [p for p in matched if p["price"] <= (budget or 9999)]
    on_sale = [p for p in matched if p["on_sale"]]
    snap_items = [p for p in matched if p["snap"]]

    clauses = [f"{opener}: {store_name}"]

    if location:
        clauses.append(f"near {location}")

    if affordable:
        sample = affordable[0]
        clauses.append(
            f"{len(affordable)} matching item(s) found "
            f"(e.g. {sample['name']} @ ${sample['price']:.2f})"
        )

    if budget and affordable:
        clauses.append(f"all within your ${budget:.0f} budget")

    if "snap" in prefs and snap_items:
        clauses.append(f"{len(snap_items)} SNAP-eligible")

    if on_sale:
        clauses.append(f"{len(on_sale)} item(s) on sale")

    if "organic" in prefs:
        org = [p for p in matched if "organic" in p["name"].lower()]
        if org:
            clauses.append(f"{len(org)} organic option(s) available")

    return ", ".join(clauses) + f". (match score: {int(score * 100)}%)"

# api

class Query(BaseModel):
    prompt: str

class Product(BaseModel):
    name: str
    brand: str
    category: str
    price: float
    regular_price: float
    on_sale: bool
    snap: bool

class StoreResult(BaseModel):
    store_id: int
    name: str
    address: str
    score: float
    products: list[Product]
    explanation: str

class Response(BaseModel):
    prompt: str
    intent: dict
    results: list[StoreResult]


@app.get("/")
def health():
    return {"status": "ok", "stores_indexed": len(store_ids)}


@app.post("/api/grocery-recs", response_model=Response)
def recommend(query: Query):
    if not query.prompt.strip():
        raise HTTPException(400, "Prompt cannot be empty.")

    intent = parse(query.prompt)

    q_vec = model.encode([intent_to_query(query.prompt, intent)], convert_to_numpy=True)
    scores = cosine_similarity(q_vec, store_vecs)[0]
    top3 = np.argsort(scores)[::-1][:3]

    results = []
    for rank, idx in enumerate(top3):
        sid = store_ids[idx]
        sim = float(scores[idx])
        row = stores[stores.store_id == sid].iloc[0]
        address = f"{row.address}, {row.city}, {row.state} {row.zip_code}"
        matched = match_products(sid, intent)

        results.append(StoreResult(
            store_id = int(sid),
            name = row.store_name,
            address = address,
            score = round(sim, 4),
            products = [Product(**p) for p in matched],
            explanation = explain(row.store_name, intent, matched, sim, rank),
        ))

    return Response(prompt=query.prompt, intent=intent, results=results)