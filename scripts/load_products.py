import os
import sqlite3
import pandas as pd

# Get path to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Move up to project root
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Paths
DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "clean", "kroger_products.csv")

print("Database path:", DB_PATH)
print("CSV path:", CSV_PATH)

# Read CSV
df = pd.read_csv(CSV_PATH)

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

processed = 0
actually_inserted = 0

for _, row in df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO products (
            product_id, product_name, brand
        ) VALUES (?, ?, ?)
    """, (
        str(row["product_id"]),
        row["item_name"],
        row["brand"]
    ))

    processed += 1

    if cursor.rowcount == 1:
        actually_inserted += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM products;")
total_rows = cursor.fetchone()[0]

conn.close()

print(f"Processed rows: {processed}")
print(f"Actually inserted: {actually_inserted}")
print(f"Total rows now in products table: {total_rows}")