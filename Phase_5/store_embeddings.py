import json
import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

# Configuration
INPUT_FILE = "../Phase 4/embeddings.json"

def main():
    # Load env from .env
    load_dotenv(dotenv_path="../.env")
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("Error: DATABASE_URL not found in .env file.")
        return

    # To handle the Nishita@152 issue, we must ensure @ is URL encoded if used in connection string
    # Supabase URLs sometimes use unquoted @ in passwords which can confuse psycopg2
    if 'Nishita@152' in database_url:
        database_url = database_url.replace('Nishita@152', 'Nishita%40152')
    
    try:
        # Connect to Postgres
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Create extension if not exists
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        
        # Register pgvector handler
        register_vector(conn)
        
        # Recreate table with correct dimensions if it exists with wrong ones
        cur.execute("DROP TABLE IF EXISTS fund_embeddings;")
        cur.execute("""
            CREATE TABLE fund_embeddings (
                id bigserial PRIMARY KEY,
                content text NOT NULL,
                url text,
                title text,
                embedding vector(3072)
            );
        """)
        conn.commit()
        
        print("Table 'fund_embeddings' verified/created.")

        # Load data
        if not os.path.exists(INPUT_FILE):
            print(f"Error: {INPUT_FILE} not found.")
            return
            
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Inserting {len(data)} embeddings...")
        
        # Clear existing data for fresh load if needed? 
        # User didn't specify, but for task completion, we'll just insert.
        # cur.execute("TRUNCATE TABLE fund_embeddings;") 
        
        for item in data:
            content = item.get("content")
            metadata = item.get("metadata", {})
            embedding = item.get("embedding")
            
            cur.execute("""
                INSERT INTO fund_embeddings (content, url, title, embedding)
                VALUES (%s, %s, %s, %s)
            """, (content, metadata.get("url"), metadata.get("title"), embedding))
        
        conn.commit()
        print(f"Successfully inserted {len(data)} embeddings into PostgreSQL.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error during vector storage process: {e}")

if __name__ == "__main__":
    main()
