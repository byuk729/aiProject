import os
import sqlite3
import pandas as pd

# paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "clean")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

total_rows = 0

for filename in os.listdir(DATA_DIR):
    if filename.endswith(".csv"):
        file_path = os.path.join(DATA_DIR, filename)
        print(f"\nChecking file: {filename}")

        try:
            df = pd.read_csv(file_path)
            print(df.columns.tolist())

            required_cols = {
                "store_id", "store_name", "address", "city",
                "state", "zip_code", "latitude", "longitude"
            }

            if not required_cols.issubset(df.columns):
                print("Skipping: not a store file")
                continue

            print("Loading store data...")

            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO stores (
                        store_id, store_name, address, city, state, zip_code, latitude, longitude
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(row["store_id"]),
                    row["store_name"],
                    row["address"],
                    row["city"],
                    row["state"],
                    str(row["zip_code"]),
                    float(row["latitude"]),
                    float(row["longitude"])
                ))

            total_rows += len(df)

        except Exception as e:
            print(f"Error reading {filename}: {e}")

conn.commit()
conn.close()

print(f"\nDone. Inserted {total_rows} rows into stores table.")