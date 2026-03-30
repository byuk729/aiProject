# This was just a test for myself to see the structure of my .csv files

import os
import pandas as pd

current_dir = os.path.dirname(__file__)

file_path = os.path.join(
    current_dir,
    "..", "..",  # go up from test → scripts → project root
    "data",
    "clean",
    "kroger_products.csv"
)

file_path = os.path.abspath(file_path)

print("Looking for:", file_path)
print("File exists:", os.path.exists(file_path))

df = pd.read_csv(file_path)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 3 rows:")
print(df.head(3))