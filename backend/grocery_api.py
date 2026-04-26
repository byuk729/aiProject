import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

BASE     = os.path.join(os.path.dirname(__file__), "../data/clean")
products = pd.concat([
    pd.read_csv(os.path.join(BASE, "kroger_products.csv")),
    pd.read_csv(os.path.join(BASE, "synthetic_products.csv")),
], ignore_index=True)
stores   = pd.read_csv(os.path.join(BASE, "stores.csv"))
products["store_id"] = products["store_id"].astype(str)
stores["store_id"]   = stores["store_id"].astype(str)
catalog  = products.merge(stores, on="store_id", how="left")

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

store_ids   = stores.store_id.tolist()
store_texts = [store_to_text(sid) for sid in store_ids]
store_vecs  = model.encode(store_texts, convert_to_numpy=True)

# product -> vector
def product_to_text(row) -> str:
    snap  = "SNAP eligible" if row.snap_eligible else "not SNAP eligible"
    sale  = f"on sale for ${row.price_promo:.2f}" if pd.notna(row.price_promo) else f"regular price ${row.price_regular:.2f}"
    brand = row.brand if pd.notna(row.brand) else "store brand"
    return (
        f"{row.item_name} by {brand} at {row.store_name}. "
        f"Category: {row.category}. "
        f"Price: {sale}. "
        f"{snap}."
    )

product_texts = catalog.apply(product_to_text, axis=1).tolist()
product_vecs  = model.encode(product_texts, convert_to_numpy=True, show_progress_bar=True)

