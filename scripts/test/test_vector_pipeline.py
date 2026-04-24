import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from data.DatabaseService import DatabaseService
from scripts.query_to_vector import parsed_query_to_vector

def run_test(parsed_query):
    db_service = DatabaseService("data/grocery.db")

    query_vector = parsed_query_to_vector(parsed_query)

    results = db_service.search_products_by_embedding(
        city="Charlottesville",
        query_vector=query_vector,
        k=5
    )

    print("\nQUERY:", parsed_query)
    print("RESULTS:")

    for r in results:
        print(r)

if __name__ == "__main__":
    test_cases = [
        {"search_term": "apples", "mode": "cheapest"},
        {"search_term": "organic apples", "mode": "cheapest"},
        {"search_term": "milk", "mode": "cheapest"},
        {"search_term": "bread", "mode": "cheapest"},
        {"search_term": "eggs", "mode": "most_expensive"},
    ]

    for test in test_cases:
        run_test(test)
        print("\n" + "="*40)