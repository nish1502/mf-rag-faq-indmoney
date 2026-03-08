import os
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Configuration
MODEL_NAME = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(MODEL_NAME)

def retrieve_context(query, top_k=3):
    """Retrieves context from PostgreSQL based on query similarity."""
    load_dotenv(dotenv_path="../.env")
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Error: Missing DATABASE_URL in .env.")
        return []

    # Handle the Nishita@152 issue
    if 'Nishita@152' in database_url:
        database_url = database_url.replace('Nishita@152', 'Nishita%40152')

    # Step 1: Embed the query locally
    try:
        query_embedding = embedding_model.encode(query).tolist()
    except Exception as e:
        print(f"Error embedding query: {e}")
        return []

    # Step 2: Search in PostgreSQL
    try:
        conn = psycopg2.connect(database_url)
        register_vector(conn)
        cur = conn.cursor()

        # Using cosine similarity (<=> is cosine distance in pgvector)
        cur.execute("""
            SELECT content, url, title, 1 - (embedding <=> %s::vector) AS similarity
            FROM fund_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (query_embedding, query_embedding, top_k))

        results = cur.fetchall()
        
        formatted_results = []
        for row in results:
            formatted_results.append({
                "content": row[0],
                "url": row[1],
                "title": row[2],
                "similarity": row[3]
            })

        cur.close()
        conn.close()
        return formatted_results

    except Exception as e:
        print(f"Error searching vector DB: {e}")
        return []

if __name__ == "__main__":
    # Test Retrieval
    test_query = "What is the exit load of SBI Small Cap Fund?"
    print(f"Testing retrieval for: '{test_query}'")
    
    contexts = retrieve_context(test_query)
    
    if not contexts:
        print("No contexts found.")
    else:
        for i, ctx in enumerate(contexts):
            print(f"\nResult {i+1} (Similarity: {ctx['similarity']:.4f}):")
            print(f"Title: {ctx['title']}")
            print(f"URL: {ctx['url']}")
            print(f"Content: {ctx['content'][:200]}...")
