import os
import sqlite3
import sys

from kroger.fetch_products import fetch_products, load_charlottesville_stores
from kroger.get_kroger_token import get_access_token

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tell Python to treat scripts/ as a module root
sys.path.append(BASE_DIR)
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "grocery.db")


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


def search_kroger_api_all_stores(search_term):
    access_token = get_access_token("product.compact")
    stores = load_charlottesville_stores()

    all_rows = []

    for store_id, address in stores:
        try:
            rows = fetch_products(search_term, store_id, access_token, limit=5)

            for row in rows:
                all_rows.append({
                    "store_id": row[0],
                    "store_address": address,
                    "query_term": row[1],
                    "product_id": row[2],
                    "upc": row[3],
                    "brand": row[4],
                    "item_name": row[5],
                    "category": row[6],
                    "price_regular": row[7],
                    "price_promo": row[8],
                    "snap_eligible": row[9],
                    "country_origin": row[10],
                    "data_source": row[11]
                })
        except Exception as e:
            print(f"API error for store {store_id}: {e}")

    return all_rows


def print_local_results(rows):
    print("\nFound in local database:")
    for row in rows:
        store_name, product_name, brand, price, promo_price = row
        print(f"{store_name} | {brand} | {product_name} | regular: {price} | promo: {promo_price}")


def print_api_results(rows):
    print("\nFound in Kroger API:")
    for item in rows:
        print(
            f"{item['store_address']} | "
            f"{item['brand']} | "
            f"{item['item_name']} | "
            f"regular: {item['price_regular']} | "
            f"promo: {item['price_promo']}"
        )


def main():
    print("Looking for DB at:", DB_PATH)
    print("Exists:", os.path.exists(DB_PATH))

    search_term = input("Enter product to search: ").strip()

    if not search_term:
        print("Error: missing search term.")
        return

    conn = sqlite3.connect(DB_PATH)

    try:
        local_results = search_local_db(conn, search_term)

        if local_results:
            print_local_results(local_results)
            return

        print("\nNo local database results found.")
        print("Searching Kroger API...")

        api_results = search_kroger_api_all_stores(search_term)

        if api_results:
            print_api_results(api_results)
        else:
            print("\nNo results found anywhere.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()