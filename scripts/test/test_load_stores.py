# This was a test for me to see if the load_stores (kroger) worked correctly

import csv

file_path = "../../clean/stores.csv"

'''
Opens stores.csv, stores it, prints header
Confirms if path/file exists, is readable, etc.
'''
with open(file_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)

print("CSV loaded successfully.")
print("Number of rows:", len(rows))
print("Header:", rows[0])