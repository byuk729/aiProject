import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

file_path = os.path.join(PROJECT_ROOT, "data", "clean", "synthetic_products.csv")

print("Looking for:", file_path)
print("File exists:", os.path.exists(file_path))

df = pd.read_csv(file_path)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 3 rows:")
print(df.head(3))