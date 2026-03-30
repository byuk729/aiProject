# temporary script or inside python shell
import sqlite3

conn = sqlite3.connect("../data/grocery.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM store_products;")

conn.commit()
conn.close()

print("Cleared store_products table")