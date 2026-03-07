import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock objects to test Phase 6 & 7 integration
from Phase_8.app import retrieve_context, generate_answer

def test_retrieval():
    print("Testing Retrieval...")
    query = "What is the exit load of SBI Small Cap Fund?"
    results = retrieve_context(query)
    assert len(results) > 0
    print(f"✅ Found {len(results)} relevant contexts.")
    for r in results:
        print(f" - {r['title']}")

def test_generation():
    print("\nTesting Generation...")
    query = "What is the exit load of SBI Small Cap Fund?"
    contexts = [
        {
            "title": "SBI Small Cap Fund Details",
            "url": "https://example.com",
            "content": "Exit load is 1% if redeemed within 1 year, nil thereafter."
        }
    ]
    response = generate_answer(query, contexts)
    assert len(response.split()) > 5
    assert "1%" in response
    print(f"✅ Response generated: {response}")

if __name__ == "__main__":
    try:
        test_retrieval()
        test_generation()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
