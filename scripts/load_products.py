import os
import sqlite3
import pandas as pd

# Get path to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Move up to project root
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Paths
DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")

CSV_PATHS = [
    os.path.join(PROJECT_ROOT, "data", "clean", "kroger_products.csv"),
    os.path.join(PROJECT_ROOT, "data", "clean", "synthetic_products.csv"),
]

print("Database path:", DB_PATH)
print("CSV files:")
for path in CSV_PATHS:
    print(" -", path, "| exists:", os.path.exists(path))

# Read and combine CSVs
dfs = []
for path in CSV_PATHS:
    df = pd.read_csv(path, dtype={"store_id": str, "product_id": str, "upc": str})
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

print(f"\nTotal raw rows from all CSVs: {len(combined_df)}")

# Keep only product columns
products_df = combined_df[["product_id", "item_name", "brand"]].copy()

# Clean
products_df["product_id"] = products_df["product_id"].astype(str).str.strip()
products_df["item_name"] = products_df["item_name"].astype(str).str.strip()
products_df["brand"] = products_df["brand"].fillna("").astype(str).str.strip()

# Drop invalid rows
products_df = products_df[
    (products_df["product_id"] != "") &
    (products_df["item_name"] != "")
]

# Remove duplicates by product_id
products_df = products_df.drop_duplicates(subset=["product_id"])

print(f"Unique products to attempt insert: {len(products_df)}")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

processed = 0
actually_inserted = 0

for _, row in products_df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO products (
            product_id, product_name, brand
        ) VALUES (?, ?, ?)
    """, (
        row["product_id"],
        row["item_name"],
        row["brand"] if row["brand"] != "" else None
    ))

    processed += 1

    if cursor.rowcount == 1:
        actually_inserted += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM products;")
total_rows = cursor.fetchone()[0]

conn.close()

print(f"\nProcessed rows: {processed}")
print(f"Actually inserted: {actually_inserted}")
print(f"Total rows now in products table: {total_rows}")