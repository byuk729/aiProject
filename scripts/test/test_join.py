import os
import sqlite3

# Get current file location (test folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# Now go into data folder
DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")

print("Looking for DB at:", DB_PATH)
print("Exists:", os.path.exists(DB_PATH))

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

search_term = input("Enter product to search: ")

cursor.execute("""
    SELECT s.store_name, p.product_name, p.brand, sp.price, sp.promo_price
    FROM store_products sp
    JOIN stores s ON sp.store_id = s.store_id
    JOIN products p ON sp.product_id = p.product_id
    WHERE p.product_name LIKE ?
    LIMIT 10
""", (f"%{search_term}%",))

rows = cursor.fetchall()

if rows:
    print("\nFound in local database:")
    for row in rows:
        print(row)
else:
    print("\nNo local database results found.")
    print("Next step: fall back to Kroger API.")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()