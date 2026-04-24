import ollama
import struct
import sqlite3
import sqlite_vec

EMBEDDING_MODEL = "nomic-embed-text"

def serialize_vector(vector):
    return struct.pack(f"{len(vector)}f", *vector)

def parsed_query_to_vector(parsed_query):
    search_term = parsed_query["search_term"]
    mode = parsed_query.get("mode", "")

    #text = f"{search_term}"
    text = f"grocery product {search_term}"

    if mode == "cheapest":
        text += " low price budget"
    elif mode == "most_expensive":
        text += " premium high quality expensive"

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=[text]
    )

    vector = response["embeddings"][0]
    return serialize_vector(vector)

def test_vector_search(parsed_query):
    # connect to DB
    db = sqlite3.connect("data/grocery.db")
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    # get query vector
    query_vector = parsed_query_to_vector(parsed_query)

    # run vector search
    results = db.execute("""
        SELECT p.product_name, p.brand, ge.distance
        FROM grocery_embeddings ge
        JOIN products p ON ge.rowid = p.rowid
        WHERE ge.embedding MATCH ?
        AND k = 5
    """, (query_vector,)).fetchall()

    db.close()
    return results

if __name__ == "__main__":
    parsed = {
        "search_term": "organic apples",
        "mode": "cheapest"
    }

    results = test_vector_search(parsed)

    for r in results:
        print(r)