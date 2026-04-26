import json
import re

from llm_pipeline import parse_user_query  # adjust if needed


# -------------------------------
# Utility: safe comparison
# -------------------------------
def compare_partial(result, expected):
    for key, val in expected.items():
        if result.get(key) != val:
            return False
    return True


# -------------------------------
# 1. BASIC CORRECTNESS TESTS
# -------------------------------
def test_basic_cases():
    print("\n===== BASIC TESTS =====")

    cases = [
        ("chicken", {"keywords": ["chicken"], "max_price": None, "snap_only": False, "on_sale": False, "brand": None}),
        ("eggs under $3", {"max_price": 3.0}),
        ("SNAP milk", {"snap_only": True}),
        ("Kroger bread on sale", {"on_sale": True, "brand": "Kroger"}),
    ]

    correct = 0

    for query, expected in cases:
        result = parse_user_query(query)

        print(f"\nQuery: {query}")
        print("Result:", result)

        if compare_partial(result, expected):
            correct += 1
        else:
            print("❌ FAILED:", expected)

    print(f"\nBasic Accuracy: {correct}/{len(cases)}")


# -------------------------------
# 2. SCHEMA VALIDATION TESTS
# -------------------------------
def test_schema():
    print("\n===== SCHEMA TESTS =====")

    queries = [
        "milk",
        "cheap eggs",
        "SNAP eligible bread",
        "Kroger milk under $4",
        "pasta night food",
    ]

    for query in queries:
        result = parse_user_query(query)

        print(f"\nQuery: {query}")
        print("Result:", result)

        assert isinstance(result, dict), "❌ Not a dict"

        required_keys = ["keywords", "max_price", "snap_only", "on_sale", "brand"]

        for key in required_keys:
            assert key in result, f"❌ Missing key: {key}"

        assert isinstance(result["keywords"], list), "❌ keywords not a list"
        assert isinstance(result["snap_only"], bool), "❌ snap_only not bool"
        assert isinstance(result["on_sale"], bool), "❌ on_sale not bool"


# -------------------------------
# 3. EDGE CASE TESTS
# -------------------------------
def test_edge_cases():
    print("\n===== EDGE CASES =====")

    queries = [
        "cheap milk",
        "milk less than $5 and on sale",
        "organic eggs",
        "something for pasta night",
        "EBT eligible cheese",
        "Kroger organic milk under $4",
    ]

    for query in queries:
        result = parse_user_query(query)

        print(f"\nQuery: {query}")
        print("Result:", result)


# -------------------------------
# 4. STRESS TEST (random-ish)
# -------------------------------
def test_stress():
    print("\n===== STRESS TEST =====")

    queries = [
        "cheap organic milk under $5 on sale",
        "i need pasta stuff",
        "something healthy",
        "best deal chicken",
        "EBT eligible snacks under $10",
        "random words blah blah milk",
        "under $2 eggs on sale kroger",
    ]

    for query in queries:
        result = parse_user_query(query)

        print(f"\nQuery: {query}")
        print("Result:", result)


# -------------------------------
# 5. JSON SAFETY TEST
# -------------------------------
def test_json_safety():
    print("\n===== JSON SAFETY =====")

    query = "milk under $5"

    result = parse_user_query(query)

    try:
        json.dumps(result)
        print("✅ JSON is valid")
    except Exception as e:
        print("❌ JSON serialization failed:", e)


# -------------------------------
# MAIN RUNNER
# -------------------------------
if __name__ == "__main__":
    print("\n🚀 RUNNING FULL PARSER TEST SUITE")

    test_basic_cases()
    test_schema()
    test_edge_cases()
    test_stress()
    test_json_safety()

    print("\n✅ DONE")