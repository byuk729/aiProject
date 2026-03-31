import requests
import json
import csv
import os

from kroger.get_kroger_token import get_access_token

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(BASE_DIR)
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)


def save_raw_json(data):
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw", "kroger")
    os.makedirs(raw_dir, exist_ok=True)

    filepath = os.path.join(raw_dir, "latest_products.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filepath


def clean_products(products, location_id, query):
    rows = []

    for product in products:
        product_id = product.get("productId")
        upc = product.get("upc")
        brand = product.get("brand")
        item_name = product.get("description")

        categories = product.get("categories", [])
        category = categories[0] if categories else None

        snap_eligible = product.get("snapEligible")
        country_origin = product.get("countryOrigin")

        items = product.get("items", [])
        price_regular = None
        price_promo = None

        if items:
            first_item = items[0]
            price_info = first_item.get("price", {})
            price_regular = price_info.get("regular")
            price_promo = price_info.get("promo")

        rows.append([
            location_id,
            query,
            product_id,
            upc,
            brand,
            item_name,
            category,
            price_regular,
            price_promo,
            snap_eligible,
            country_origin,
            "real_kroger"
        ])

    return rows


def fetch_products(query, location_id, access_token, limit=10):
    url = "https://api.kroger.com/v1/products"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "filter.term": query,
        "filter.locationId": location_id,
        "filter.limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    save_raw_json(data)

    products = data.get("data", [])
    rows = clean_products(products, location_id, query)

    return rows


def print_products_by_store(store_address, rows):
    print(f"\n{store_address}:")

    if not rows:
        print("- No products found")
        return

    for row in rows:
        brand = row[4]
        item_name = row[5]
        price_regular = row[7]
        price_promo = row[8]

        print(f"- {brand} | {item_name} | regular: {price_regular} | promo: {price_promo}")


def load_charlottesville_stores(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(PROJECT_ROOT, "data", "clean", "stores.csv")

    stores = []

    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            city = row["city"].strip().lower()
            store_id = row["store_id"].strip()
            store_name = row["store_name"].strip()
            address = row["address"].strip()

            if city != "charlottesville":
                continue

            # skip synthetic stores for Kroger API calls
            if store_id.startswith("SYN_"):
                continue

            stores.append((store_id, store_name, address))

    return stores

if __name__ == "__main__":
    access_token = get_access_token("product.compact")

    query = input("Enter grocery item: ").strip()

    if not query:
        print("Error: Missing grocery item.")
        raise SystemExit

    stores = load_charlottesville_stores()

    if not stores:
        print("No Charlottesville stores found.")
        raise SystemExit

    all_rows = []

    for store_id, address in stores:
        rows = fetch_products(query, store_id, access_token, limit=10)
        print_products_by_store(address, rows)
        all_rows.extend(rows)

    print(f"\nFetched {len(all_rows)} cleaned rows total.")