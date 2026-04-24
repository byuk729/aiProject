import ollama
import struct

EMBEDDING_MODEL = "nomic-embed-text"

def serialize_vector(vector):
    return struct.pack(f"{len(vector)}f", *vector)

def parsed_query_to_vector(parsed_query):
    search_term = parsed_query["search_term"]
    mode = parsed_query.get("mode", "")

    text = f"{search_term}"

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

if __name__ == "__main__":
    parsed = {
        "search_term": "organic apples",
        "mode": "cheapest"
    }

    vec = parsed_query_to_vector(parsed)
    print(type(vec))
    print(len(vec))