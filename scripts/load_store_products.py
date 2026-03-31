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

# Keep only needed columns
store_products_df = combined_df[["store_id", "product_id", "price_regular", "price_promo"]].copy()

# Clean
store_products_df["store_id"] = store_products_df["store_id"].astype(str).str.strip()
store_products_df["product_id"] = store_products_df["product_id"].astype(str).str.strip()

def clean_price(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        value = value.replace("$", "").replace(",", "").strip()
        if value == "":
            return None
    return float(value)

store_products_df["price_regular"] = store_products_df["price_regular"].apply(clean_price)
store_products_df["price_promo"] = store_products_df["price_promo"].apply(clean_price)

# Drop invalid rows
store_products_df = store_products_df[
    (store_products_df["store_id"] != "") &
    (store_products_df["product_id"] != "")
]

# Remove duplicate store-product pairs before insert
store_products_df = store_products_df.drop_duplicates(subset=["store_id", "product_id"])

print(f"Unique store-product rows to attempt insert: {len(store_products_df)}")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

processed = 0
actually_inserted = 0
skipped_missing_store = 0
skipped_missing_product = 0

for _, row in store_products_df.iterrows():
    store_id = row["store_id"]
    product_id = row["product_id"]
    price = row["price_regular"]
    promo_price = row["price_promo"]

    # make sure store exists
    cursor.execute("SELECT 1 FROM stores WHERE store_id = ?", (store_id,))
    if cursor.fetchone() is None:
        skipped_missing_store += 1
        continue

    # make sure product exists
    cursor.execute("SELECT 1 FROM products WHERE product_id = ?", (product_id,))
    if cursor.fetchone() is None:
        skipped_missing_product += 1
        continue

    cursor.execute("""
        INSERT OR IGNORE INTO store_products (
            store_id, product_id, price, promo_price
        ) VALUES (?, ?, ?, ?)
    """, (
        store_id,
        product_id,
        price,
        promo_price
    ))

    processed += 1

    if cursor.rowcount == 1:
        actually_inserted += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM store_products;")
total_rows = cursor.fetchone()[0]

conn.close()

print(f"\nProcessed valid rows: {processed}")
print(f"Actually inserted: {actually_inserted}")
print(f"Skipped missing store: {skipped_missing_store}")
print(f"Skipped missing product: {skipped_missing_product}")
print(f"Total rows now in store_products table: {total_rows}")