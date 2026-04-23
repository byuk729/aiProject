import os
import sqlite3
import sqlite_vec
import ollama
import struct


def get_db():
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(cur_dir, "..", "data")
    database_path = os.path.join(data_dir, "grocery.db")

    db = sqlite3.connect(database_path)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


def create_vector_table():
    db = get_db()

    db.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS grocery_embeddings USING vec0(
            embedding float[1536]
        )
    """
    )

    db.commit()
    db.close()


if __name__ == "__main__":
    create_vector_table()
