import os
import sys
import struct
import sqlite3
import sqlite_vec
import ollama

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..", "..")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")

EMBEDDING_MODEL = "nomic-embed-text"


def _serialize_vector(vector):
    return struct.pack(f"{len(vector)}f", *vector)


def _embed_query(text: str) -> bytes:
    response = ollama.embed(model=EMBEDDING_MODEL, input=[f"search_query: {text}"])
    return _serialize_vector(response["embeddings"][0])


def _db_has_vector_table(db: sqlite3.Connection) -> bool:
    row = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='grocery_embeddings'"
    ).fetchone()
    return row is not None


def search_normal_db(city: str, search_term: str, limit: int = 10) -> list[dict]:
    """LIKE-based search against the regular products table."""
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT
            s.store_name,
            p.product_name,
            p.brand,
            sp.price,
            sp.promo_price
        FROM store_products sp
        JOIN stores s ON sp.store_id = s.store_id
        JOIN products p ON sp.product_id = p.product_id
        WHERE s.city = ?
          AND LOWER(p.product_name) LIKE LOWER(?)
        ORDER BY p.product_name, s.store_name
        LIMIT ?
        """,
        (city, f"%{search_term}%", limit),
    )
    rows = cursor.fetchall()
    db.close()
    return [
        {
            "store_name": r[0],
            "product_name": r[1],
            "brand": r[2],
            "price": r[3],
            "promo_price": r[4],
            "source": "db",
        }
        for r in rows
    ]


def search_vector_db(city: str, search_term: str, k: int = 10) -> list[dict]:
    """Semantic search using the sqlite-vec grocery_embeddings table."""
    db = sqlite3.connect(DB_PATH)
    try:
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
    except AttributeError:
        db.close()
        raise RuntimeError(
            "SQLite extension loading is not supported on this platform. "
            "Run on Linux (UVA HPC) where sqlite3 is compiled with extension support."
        )

    if not _db_has_vector_table(db):
        db.close()
        raise RuntimeError(
            "Vector table 'grocery_embeddings' does not exist. "
            "Run scripts/create_vector_db.py first."
        )

    query_vector = _embed_query(search_term)

    # searchs by KNN first, then join and filter by city
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT
            s.store_name,
            p.product_name,
            p.brand,
            sp.price,
            sp.promo_price,
            vec_search.distance
        FROM (
            SELECT rowid, distance
            FROM grocery_embeddings
            WHERE embedding MATCH ?
              AND k = ?
        ) vec_search
        JOIN products p ON p.rowid = vec_search.rowid
        JOIN store_products sp ON sp.product_id = p.product_id
        JOIN stores s ON s.store_id = sp.store_id
        WHERE s.city = ?
        ORDER BY vec_search.distance ASC
        LIMIT ?
        """,
        (query_vector, k, city, k),
    )
    rows = cursor.fetchall()
    db.close()
    return [
        {
            "store_name": r[0],
            "product_name": r[1],
            "brand": r[2],
            "price": r[3],
            "promo_price": r[4],
            "distance": r[5],
            "source": "vector",
        }
        for r in rows
    ]


def search(city: str, search_term: str, k: int = 10) -> list[dict]:
    """
    Hybrid search: runs both normal DB and vector DB, merges results.
    Exact DB matches come first, followed by vector matches not already in the DB results.
    """
    db_results = search_normal_db(city, search_term, limit=k)

    try:
        vector_results = search_vector_db(city, search_term, k=k)
    except RuntimeError:
        return db_results

    seen = {(r["store_name"], r["product_name"]) for r in db_results}
    extra = [r for r in vector_results if (r["store_name"], r["product_name"]) not in seen]

    return (db_results + extra)[:k]
