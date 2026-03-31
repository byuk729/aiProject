import os
import sys
import sqlite3

# Fix import path so kroger/ works
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)

from kroger.fetch_products import fetch_products, load_charlottesville_stores
from kroger.get_kroger_token import get_access_token

DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")


# ---------------------------
# LOCAL DATABASE SEARCH
# ---------------------------
def search_local_db(conn, search_term):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.store_name, p.product_name, p.brand, sp.price, sp.promo_price
        FROM store_products sp
        JOIN stores s ON sp.store_id = s.store_id
        JOIN products p ON sp.product_id = p.product_id
        WHERE LOWER(p.product_name) LIKE LOWER(?)
        ORDER BY p.product_name, s.store_name
        LIMIT 20
    """, (f"%{search_term}%",))

    return cursor.fetchall()


# ---------------------------
# KROGER API SEARCH
# ---------------------------
def search_kroger_api_all_stores(search_term):
    access_token = get_access_token("product.compact")
    stores = load_charlottesville_stores()

    all_rows = []

    for store_id, store_name, address in stores:
        try:
            rows = fetch_products(search_term, store_id, access_token, limit=5)

            for row in rows:
                all_rows.append({
                    "store_name": store_name,
                    "brand": row[4],
                    "item_name": row[5],
                    "price_regular": row[7],
                    "price_promo": row[8],
                })

        except Exception as e:
            print(f"API error for store {store_id}: {e}")

    return all_rows


# ---------------------------
# PRINT FUNCTIONS
# ---------------------------
def print_local_results(rows):
    print("\n=== Local Database Results ===")
    for store_name, product_name, brand, price, promo_price in rows:
        print(f"{store_name} | {brand} | {product_name} | ${price} | promo: {promo_price}")


def print_api_results(rows):
    print("\n=== Kroger API Results ===")
    for item in rows:
        print(
            f"{item['store_name']} | "
            f"{item['brand']} | "
            f"{item['item_name']} | "
            f"${item['price_regular']} | promo: {item['price_promo']}"
        )


# ---------------------------
# MAIN
# ---------------------------
def main():
    print("Looking for DB at:", DB_PATH)
    print("Exists:", os.path.exists(DB_PATH))

    search_term = input("Enter product to search: ").strip()

    if not search_term:
        print("Error: missing search term.")
        return

    conn = sqlite3.connect(DB_PATH)

    try:
        # 1. LOCAL SEARCH
        local_results = search_local_db(conn, search_term)

        if local_results:
            print_local_results(local_results)
        else:
            print("\nNo local database results found.")

        # 2. ALWAYS CALL API (NEW BEHAVIOR)
        print("\nSearching Kroger API...")
        api_results = search_kroger_api_all_stores(search_term)

        if api_results:
            print_api_results(api_results)
        else:
            print("\nNo results found from Kroger API.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()