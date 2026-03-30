import os
import sqlite3

# Get the directory where THIS script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level (from scripts → aiProject)
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Create data folder inside project root
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Full path to database
DB_PATH = os.path.join(DATA_DIR, "grocery.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create stores table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stores (
    store_id TEXT PRIMARY KEY,
    store_name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    latitude REAL,
    longitude REAL
)
""")

# Create products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    brand TEXT
)
""")

# Create store_products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS store_products (
    store_id TEXT,
    product_id TEXT,
    price REAL,
    promo_price REAL,
    PRIMARY KEY (store_id, product_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully.")