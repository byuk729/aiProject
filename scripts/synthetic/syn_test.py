import csv

def search_synthetic_data():
    query = input("Enter grocery item: ").strip().lower()

    if not query:
        print("Error: Missing product.")
        return

    store_input = input("Enter store (wegmans / walmart / x for both): ").strip().lower()

    file_path = "../../data/clean/synthetic_products.csv"
    matches = []

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row_query = row["query_term"].strip().lower()
            row_store = row["store_id"].strip().lower()

            # Match product
            if row_query != query:
                continue

            # Match store
            if store_input == "wegmans" and row_store != "syn_wegmans":
                continue
            elif store_input == "walmart" and row_store != "syn_walmart":
                continue
            elif store_input != "x" and store_input not in ["wegmans", "walmart"]:
                print("Invalid store option.")
                return

            matches.append(row)

    if not matches:
        print("Item not in data")
        return

    print(f"\nFound {len(matches)} matching products:\n")

    current_store = None

    for row in matches:
        store = row["store_id"]

        # Group by store
        if store != current_store:
            print(f"\n=== {store} ===")
            current_store = store

        print(
            f"{row['brand']} | "
            f"{row['item_name']} | "
            f"regular: {row['price_regular']} | "
            f"promo: {row['price_promo']}"
        )

if __name__ == "__main__":
    search_synthetic_data()