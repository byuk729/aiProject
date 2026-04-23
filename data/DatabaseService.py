import sqlite3
import sqlite_vec


class DatabaseService:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_connection(self):
        db = sqlite3.connect(self.db_path)
        return db

    def get_all_products_from_city(self, city):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT
                s.store_name,
                p.product_name,
                p.brand,
                sp.price,
                sp.promo_price
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            JOIN products p
                ON sp.product_id = p.product_id
            WHERE s.city = ?
        """
        cursor.execute(query, (city,))
        results = cursor.fetchall()
        db.close()
        return results

    def get_sorted_products_from_city(self, city, product_name):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT
                s.store_name,
                p.product_name,
                p.brand,
                sp.price,
                sp.promo_price
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            JOIN products p
                ON p.product_id = sp.product_id
            WHERE s.city = ?
              AND p.product_name = ?
            ORDER BY sp.price ASC
        """
        cursor.execute(query, (city, product_name))
        results = cursor.fetchall()
        db.close()
        return results

    def get_stores_and_brands(self, city, brand):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT
                s.store_name,
                p.product_name,
                p.brand,
                sp.price,
                sp.promo_price
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            JOIN products p
                ON p.product_id = sp.product_id
            WHERE s.city = ?
              AND p.brand = ?
            ORDER BY sp.price ASC
        """
        cursor.execute(query, (city, brand))
        results = cursor.fetchall()
        db.close()
        return results

    def get_stores_for_product(self, city, product_name):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT DISTINCT
                s.store_id,
                s.store_name,
                s.address,
                s.city,
                s.state,
                s.zip_code
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            JOIN products p
                ON p.product_id = sp.product_id
            WHERE s.city = ?
              AND p.product_name = ?
            ORDER BY s.store_name ASC
        """
        cursor.execute(query, (city, product_name))
        results = cursor.fetchall()
        db.close()
        return results

    def get_best_promos_from_city(self, city):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT
                s.store_name,
                p.product_name,
                p.brand,
                sp.price,
                sp.promo_price
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            JOIN products p
                ON p.product_id = sp.product_id
            WHERE s.city = ?
              AND sp.promo_price IS NOT NULL
              AND sp.promo_price < sp.price
            ORDER BY (sp.price - sp.promo_price) DESC
        """
        cursor.execute(query, (city,))
        results = cursor.fetchall()
        db.close()
        return results

    def get_cheapest_product_from_city(self, city, product_name):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT
                s.store_name,
                p.product_name,
                p.brand,
                sp.price,
                sp.promo_price
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            JOIN products p
                ON p.product_id = sp.product_id
            WHERE s.city = ?
              AND p.product_name = ?
            ORDER BY sp.price ASC
            LIMIT 1
        """
        cursor.execute(query, (city, product_name))
        result = cursor.fetchone()
        db.close()
        return result

    def get_products_under_price_from_city(self, city, max_price):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT
                s.store_name,
                p.product_name,
                p.brand,
                sp.price,
                sp.promo_price
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            JOIN products p
                ON p.product_id = sp.product_id
            WHERE s.city = ?
              AND (
                    sp.price <= ?
                    OR (sp.promo_price IS NOT NULL AND sp.promo_price <= ?)
                  )
            ORDER BY
                CASE
                    WHEN sp.promo_price IS NOT NULL AND sp.promo_price < sp.price
                    THEN sp.promo_price
                    ELSE sp.price
                END ASC
        """
        cursor.execute(query, (city, max_price, max_price))
        results = cursor.fetchall()
        db.close()
        return results

    def get_product_count_by_store(self, city):
        db = self.create_connection()
        cursor = db.cursor()
        query = """
            SELECT
                s.store_name,
                COUNT(sp.product_id) AS product_count
            FROM stores s
            JOIN store_products sp
                ON s.store_id = sp.store_id
            WHERE s.city = ?
            GROUP BY s.store_id, s.store_name
            ORDER BY product_count DESC
        """
        cursor.execute(query, (city,))
        results = cursor.fetchall()
        db.close()
        return results
