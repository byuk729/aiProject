import requests
import base64
import json
import csv
import os

from get_kroger_token import get_access_token

ACCESS_TOKEN = get_access_token("product.compact")

# Saves raw data to file before cleaning
def save_raw_json(data):
    os.makedirs("../../data/raw/kroger", exist_ok=True)

    filepath = "../../data/raw/kroger/latest_products.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filepath

# Cleans raw product data into structured rows 
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

# Saves cleaned data into CSV file
def save_clean_csv(rows, output_file="../../data/clean/kroger_products.csv"):
    os.makedirs("../../data/clean", exist_ok=True)

    file_exists = os.path.exists(output_file)

    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "store_id",
                "query_term",
                "product_id",
                "upc",
                "brand",
                "item_name",
                "category",
                "price_regular",
                "price_promo",
                "snap_eligible",
                "country_origin",
                "data_source"
            ])

        writer.writerows(rows)

# Main function; calles Kroger API
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

# Helper function: prints products by store
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

# Helper function: loads all charlottesville stores
def load_charlottesville_stores(csv_path="../../data/clean/stores.csv"):
    stores = []

    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Only include Charlottesville stores
            if row["city"].lower() == "charlottesville":
                store_id = row["store_id"]
                address = row["address"]

                stores.append((store_id, address))

    return stores

if __name__ == "__main__":
    ACCESS_TOKEN = get_access_token("product.compact")

    query = input("Enter grocery item: ").strip()

    if not query:
        print("Error: Missing grocery item.")
        exit()

    # Load stores from CSV instead of hardcoding
    stores = load_charlottesville_stores()

    if not stores:
        print("No Charlottesville stores found.")
        exit()

    all_rows = []

    for store_id, address in stores:
        rows = fetch_products(query, store_id, ACCESS_TOKEN, limit=10)

        #print_products_by_store(address, rows)

        all_rows.extend(rows)

    save_clean_csv(all_rows)

    print(f"\nSaved {len(all_rows)} cleaned rows total.")