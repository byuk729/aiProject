import os
import sqlite3
import struct
import sqlite_vec
import ollama


EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768
BATCH_SIZE = 32


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


def build_product_text(product_name, brand, category=None):
    parts = [product_name]
    if brand:
        parts.append(f"by {brand}")
    if category:
        parts.append(f"category: {category}")
    return "search_document: " + ", ".join(parts)


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def create_vector_table(db):
    db.execute(
        f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS grocery_embeddings USING vec0(
            embedding float[{EMBEDDING_DIM}]
        )
        """
    )
    db.commit()


def populate_embeddings():
    db = get_db()
    create_vector_table(db)

    products = db.execute(
        """
        SELECT p.rowid, p.product_name, p.brand, p.category
        FROM products p
        LEFT JOIN grocery_embeddings ge
          ON p.rowid = ge.rowid
        WHERE ge.rowid IS NULL
        """
    ).fetchall()

    total = len(products)
    print(f"Need to embed {total} products")

    for batch_num, batch in enumerate(chunked(products, BATCH_SIZE), start=1):
        texts = [build_product_text(product_name, brand, category) for _, product_name, brand, category in batch]

        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=texts
        )
        embeddings = response["embeddings"]

        rows_to_insert = [
            (rowid, serialize_vector(vector))
            for (rowid, _, _, _), vector in zip(batch, embeddings)
        ]

        db.executemany(
            "INSERT OR REPLACE INTO grocery_embeddings(rowid, embedding) VALUES (?, ?)",
            rows_to_insert
        )
        db.commit()

        print(f"Finished batch {batch_num}: embedded {min(batch_num * BATCH_SIZE, total)}/{total}")

    db.close()
    print("Done.")

if __name__ == "__main__":
    populate_embeddings()
