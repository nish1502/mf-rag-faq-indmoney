import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
INPUT_FILE = "../Phase 2/cleaned_documents.json"
OUTPUT_FILE = "chunks.json"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run Phase 2 cleaning script first.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Chunking {len(documents)} cleaned documents...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunked_docs = []
    
    for doc in documents:
        url = doc.get("url", "")
        title = doc.get("title", "Untitled")
        content = doc.get("content", "")
        
        # Split text into chunks
        chunks = splitter.split_text(content)
        
        for chunk in chunks:
            chunked_docs.append({
                "content": chunk,
                "metadata": {
                    "url": url,
                    "title": title
                }
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunked_docs, f, indent=4, ensure_ascii=False)

    print(f"Chunking complete. Created {len(chunked_docs)} chunks in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
