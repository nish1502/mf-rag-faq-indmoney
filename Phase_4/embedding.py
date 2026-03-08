import json
import os
import time
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from tqdm import tqdm

# Configuration
INPUT_FILE = "../Phase_3/chunks.json"
OUTPUT_FILE = "embeddings.json"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    # Load API key from .env file
    load_dotenv(dotenv_path="../.env")
    # Initialize local model
    embedding_model = SentenceTransformer(MODEL_NAME)

    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run Phase 3 chunking script first.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Generating embeddings for {len(chunks)} chunks using {MODEL_NAME}...")
    
    embedded_data = []
    
    # Process in batches to avoid rate limits if necessary, 
    # but for ~100 chunks, a direct loop is usually fine with minor delays
    for item in tqdm(chunks):
        content = item.get("content", "")
        metadata = item.get("metadata", {})
        
        try:
            # Generate embedding locally
            embedding = embedding_model.encode(content).tolist()
            
            embedded_data.append({
                "content": content,
                "metadata": metadata,
                "embedding": embedding
            })
            
            # No delay needed for local model
            # time.sleep(0.1)
            
        except Exception as e:
            print(f"\nError generating embedding for chunk: {e}")
            continue

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, indent=4, ensure_ascii=False)

    print(f"\nEmbedding complete. Created {len(embedded_data)} embedded chunks in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
