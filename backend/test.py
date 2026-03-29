"""
test_grocery_api.py
Run with: python test_grocery_api.py
No server needed — imports and calls the functions directly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from grocery_api import parse, intent_to_query, match_products, explain, model, store_vecs, store_ids, stores
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# =============================================================================
# HELPER — runs the full pipeline for a prompt and prints results
# =============================================================================

def run_test(label: str, prompt: str):
    print("\n" + "=" * 60)
    print(f"TEST: {label}")
    print(f"PROMPT: \"{prompt}\"")
    print("=" * 60)

    # 1. Parse intent
    intent = parse(prompt)
    print(f"\n[Intent Parsed]")
    print(f"  Items:    {intent['items']}")
    print(f"  Budget:   {intent['budget']}")
    print(f"  Location: {intent['location']}")
    print(f"  Prefs:    {intent['prefs']}")

    # 2. Embed query
    query_str = intent_to_query(prompt, intent)
    q_vec     = model.encode([query_str], convert_to_numpy=True)

    # 3. Cosine similarity
    scores = cosine_similarity(q_vec, store_vecs)[0]
    top3   = np.argsort(scores)[::-1][:3]

    # 4. Print results
    print(f"\n[Top 3 Store Matches]")
    for rank, idx in enumerate(top3):
        sid     = store_ids[idx]
        sim     = float(scores[idx])
        row     = stores[stores.store_id == sid].iloc[0]
        matched = match_products(sid, intent)
        exp     = explain(row.store_name, intent, matched, sim, rank)

        print(f"\n  #{rank + 1} {row.store_name} (score: {int(sim * 100)}%)")
        print(f"      {row.address}, {row.city}")
        print(f"      {exp}")
        print(f"      Products:")
        for p in matched[:3]:
            sale_tag = " [SALE]" if p["on_sale"] else ""
            snap_tag = " [SNAP]" if p["snap"] else ""
            print(f"        - {p['name']} | ${p['price']:.2f}{sale_tag}{snap_tag}")

# =============================================================================
# TEST CASES
# =============================================================================

if __name__ == "__main__":

    run_test(
        "Basic item + location + budget",
        "I need milk near Barracks Road, budget $10"
    )

    run_test(
        "Organic preference",
        "looking for organic milk, budget $8"
    )

    run_test(
        "SNAP / EBT user",
        "I use EBT and need apples and milk"
    )

    run_test(
        "Sale items + location",
        "cheapest light bulbs near Rio Hill"
    )

    run_test(
        "Multiple items, no budget",
        "I need apples and whole milk"
    )

    run_test(
        "Budget only, no items",
        "I have $5 to spend on groceries"
    )

    run_test(
        "Location only",
        "what stores are near Hollymead"
    )

    run_test(
        "Vague prompt",
        "I need to go grocery shopping"
    )

    print("\n" + "=" * 60)
    print("All tests complete.")
    print("=" * 60)