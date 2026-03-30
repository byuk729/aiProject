import csv
import os
import random

def generate_synthetic_data():
    os.makedirs("../../data/clean", exist_ok=True)

    stores = {
        "SYN_WEGMANS": {
            "brand_default": "Wegmans",
            "price_multiplier": 1.15
        },
        "SYN_WALMART": {
            "brand_default": "Great Value",
            "price_multiplier": 0.90
        }
    }

    product_catalog = {
        "milk": {
            "category": "Dairy",
            "country_origin": "UNITED STATES",
            "price_range": (3.25, 6.50),
            "items": [
                "Whole Milk", "2% Milk", "1% Milk", "Skim Milk", "Organic Whole Milk",
                "Lactose Free Milk", "Chocolate Milk", "Almond Milk", "Oat Milk", "Soy Milk"
            ]
        },
        "eggs": {
            "category": "Dairy",
            "country_origin": "UNITED STATES",
            "price_range": (3.50, 8.00),
            "items": [
                "Eggs (Dozen)", "Large Brown Eggs", "Cage Free Eggs", "Organic Eggs",
                "Extra Large Eggs", "18 Count Eggs"
            ]
        },
        "bread": {
            "category": "Bakery",
            "country_origin": "UNITED STATES",
            "price_range": (2.00, 5.50),
            "items": [
                "White Bread", "Wheat Bread", "Sourdough Bread", "Multigrain Bread",
                "Italian Bread", "Texas Toast", "Bagels", "Hamburger Buns"
            ]
        },
        "apples": {
            "category": "Produce",
            "country_origin": "UNITED STATES",
            "price_range": (1.50, 4.50),
            "items": [
                "Gala Apples", "Fuji Apples", "Honeycrisp Apples", "Granny Smith Apples",
                "Red Delicious Apples", "Pink Lady Apples"
            ]
        },
        "bananas": {
            "category": "Produce",
            "country_origin": "ECUADOR",
            "price_range": (0.60, 2.00),
            "items": [
                "Bananas", "Organic Bananas", "Banana Bunch", "Mini Bananas"
            ]
        },
        "rice": {
            "category": "Pantry",
            "country_origin": "UNITED STATES",
            "price_range": (2.00, 7.00),
            "items": [
                "White Rice", "Brown Rice", "Jasmine Rice", "Basmati Rice",
                "Long Grain Rice", "Instant Rice"
            ]
        },
        "pasta": {
            "category": "Pantry",
            "country_origin": "UNITED STATES",
            "price_range": (1.25, 4.50),
            "items": [
                "Spaghetti", "Penne", "Rotini", "Fettuccine",
                "Elbow Macaroni", "Angel Hair Pasta"
            ]
        },
        "chicken": {
            "category": "Meat",
            "country_origin": "UNITED STATES",
            "price_range": (4.50, 11.00),
            "items": [
                "Chicken Breast", "Chicken Thighs", "Chicken Wings", "Ground Chicken",
                "Chicken Tenders", "Whole Chicken"
            ]
        },
        "cheese": {
            "category": "Dairy",
            "country_origin": "UNITED STATES",
            "price_range": (2.50, 6.50),
            "items": [
                "Cheddar Cheese", "Mozzarella Cheese", "Swiss Cheese", "Pepper Jack Cheese",
                "Shredded Cheese", "American Cheese Slices"
            ]
        },
        "yogurt": {
            "category": "Dairy",
            "country_origin": "UNITED STATES",
            "price_range": (0.90, 6.00),
            "items": [
                "Greek Yogurt", "Vanilla Yogurt", "Strawberry Yogurt", "Plain Yogurt",
                "Low Fat Yogurt", "Organic Yogurt"
            ]
        }
    }

    rows = []
    next_product_id = 200000001
    next_upc = 800000000001

    for store_id, store_info in stores.items():
        for query_term, info in product_catalog.items():
            category = info["category"]
            country_origin = info["country_origin"]
            min_price, max_price = info["price_range"]
            item_choices = info["items"]

            for _ in range(30):
                item_name = random.choice(item_choices)
                base_price = random.uniform(min_price, max_price)
                price_regular = round(base_price * store_info["price_multiplier"], 2)

                if random.random() < 0.3:
                    price_promo = round(price_regular - random.uniform(0.25, 1.25), 2)
                    if price_promo <= 0:
                        price_promo = None
                else:
                    price_promo = None

                brand = store_info["brand_default"]

                if store_id == "SYN_WALMART" and category == "Produce":
                    brand = "Freshness Guaranteed"
                elif store_id == "SYN_WALMART" and category == "Meat":
                    brand = "Marketside"
                elif store_id == "SYN_WALMART" and category == "Dairy":
                    brand = "Great Value"

                rows.append([
                    store_id,
                    query_term,
                    str(next_product_id),
                    str(next_upc),
                    brand,
                    item_name,
                    category,
                    price_regular,
                    price_promo,
                    True,
                    country_origin,
                    "synthetic"
                ])

                next_product_id += 1
                next_upc += 1

    output_file = "../../data/clean/synthetic_products.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
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

    print(f"Generated {len(rows)} synthetic rows in {output_file}")

if __name__ == "__main__":
    generate_synthetic_data()