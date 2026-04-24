"""
Run this after create_vector_db.py to verify that product rowids and
embedding rowids are properly aligned. Mismatches mean a vector for
one product is mapped to the wrong product.
"""
import os
import sqlite3
import sqlite_vec

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "grocery.db")


def main():
    db = sqlite3.connect(DB_PATH)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    rows = db.execute(
        """
        SELECT p.rowid AS product_rowid, ge.rowid AS embedding_rowid, p.product_name
        FROM products p
        LEFT JOIN grocery_embeddings ge ON p.rowid = ge.rowid
        ORDER BY p.rowid
        LIMIT 20
        """
    ).fetchall()

    print(f"{'product_rowid':<16} {'embedding_rowid':<18} product_name")
    print("-" * 70)
    mismatches = 0
    for product_rowid, embedding_rowid, name in rows:
        match = "OK" if product_rowid == embedding_rowid else "MISMATCH"
        if match == "MISMATCH":
            mismatches += 1
        print(f"{str(product_rowid):<16} {str(embedding_rowid):<18} {name}  [{match}]")

    print()
    total_products = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_embeddings = db.execute("SELECT COUNT(*) FROM grocery_embeddings").fetchone()[0]
    print(f"Total products:   {total_products}")
    print(f"Total embeddings: {total_embeddings}")
    if total_products != total_embeddings:
        print("WARNING: counts differ — some products are missing embeddings.")
    if mismatches:
        print(f"WARNING: {mismatches} rowid mismatches found in sampled rows.")
    else:
        print("All sampled rowids look aligned.")

    db.close()


if __name__ == "__main__":
    main()
