import os
import re
import sqlite3
import struct
import sqlite_vec
import ollama


EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768


def get_db():
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(cur_dir, "..", "data")
    db_path = os.path.join(data_dir, "grocery.db")

    db = sqlite3.connect(db_path)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


def serialize_vector(vector):
    return struct.pack(f"{len(vector)}f", *vector)


def normalize_text(text):
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def build_product_text(product_name, brand):
    if brand:
        text = f"{product_name} by {brand}"
    else:
        text = product_name
    return normalize_text(text)


def reset_vector_table(db):
    db.execute("DROP TABLE IF EXISTS grocery_embeddings")
    db.execute(
        f"""
        CREATE VIRTUAL TABLE grocery_embeddings USING vec0(
            embedding float[{EMBEDDING_DIM}]
        )
        """
    )
    db.commit()


def populate_embeddings():
    db = get_db()
    reset_vector_table(db)

    products = db.execute(
        """
        SELECT p.rowid, p.product_name, p.brand
        FROM products p
        ORDER BY p.rowid ASC
        """
    ).fetchall()

    total = len(products)
    print(f"Need to embed {total} products")

    for index, (rowid, product_name, brand) in enumerate(products, start=1):
        normalized_text = build_product_text(product_name, brand)

        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=[normalized_text]
        )
        vector = response["embeddings"][0]

        db.execute(
            "INSERT OR REPLACE INTO grocery_embeddings(rowid, embedding) VALUES (?, ?)",
            (rowid, serialize_vector(vector))
        )
        db.commit()

        print(
            f"[{index}/{total}] rowid={rowid} "
            f"product_name={product_name} "
            f"brand={brand} "
            f"normalized_text={normalized_text}"
        )

    db.close()
    print("Done.")


if __name__ == "__main__":
    populate_embeddings()
