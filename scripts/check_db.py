import os
import sqlite3

# Get absolute path to THIS script file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Move up one level to project root (scripts → project root)
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Build full path to the database file
DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# List of tables we want to inspect
tables = ["stores", "products", "store_products"]

# Loop through each table and print useful info
for table in tables:
    print(f"\n--- {table.upper()} ---")

    # 1. Get column info using SQLite metadata
    # PRAGMA table_info returns details about each column
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()

    print("Columns:")
    for col in columns:
        print(col[1])  # col[1] = column name

    # 2. Show first 10 rows from the table
    cursor.execute(f"SELECT * FROM {table} LIMIT 10;")
    rows = cursor.fetchall()

    print("\nSample rows:")
    for row in rows:
        print(row)

    # 3. Count total number of rows in the table
    cursor.execute(f"SELECT COUNT(*) FROM {table};")
    count = cursor.fetchone()[0]

    print(f"\nTotal rows: {count}")

# Close database connection (always do this)
conn.close()