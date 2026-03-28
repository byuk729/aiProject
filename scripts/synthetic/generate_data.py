import csv
import os
import random

def generate_synthetic_data():
    synthetic_stores = {
        "SYN_WEGMANS": "Wegmans Charlottesville",
        "SYN_WALMART": "Walmart Charlottesville"
    }

    print("Generating synthetic data for these stores:")
    for store_id, store_name in synthetic_stores.items():
        print(store_id, "-", store_name)

if __name__ == "__main__":
    generate_synthetic_data()