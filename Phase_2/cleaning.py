import json
import os
import re

# Configuration
INPUT_FILE = "../Phase 1/raw_documents.json"
OUTPUT_FILE = "cleaned_documents.json"

def clean_text(text):
    """Refined cleaning for mutual fund data."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Noise tags (SBI Specific and General)
    noise_patterns = [
        r"Add to Cart",
        r"Proceed to Invest",
        r"Enter SIP Amount",
        r"view details",
        r"Min\. Amount Rs\.",
        r"Compare Fund",
        r"Invest",
        r"Min SIP Amount",
        r"Historical NAV",
        r"Performance may or may not be sustained in future",
        r"Product Label This product is suitable for investors who are seeking",
        r"Investors should consult their financial advisors if in doubt whether the product is suitable for them",
        r"IDCW History",
        r"Demat Option",
        r"By opting out of SIP top-up, you lose out on multiplying your wealth",
        r"Setup Auto Transfer",
        r"NEW LAUNCH",
        r"KNOW MORE",
        r"SIF LAUNCH"
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
    return text.strip()

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Ensure Phase 1 scraper was successful.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Cleaning {len(documents)} documents...")
    
    cleaned_docs = []
    for doc in documents:
        cleaned_content = clean_text(doc.get("content", ""))
        if cleaned_content:
            cleaned_docs.append({
                "url": doc.get("url"),
                "title": doc.get("title"),
                "content": cleaned_content
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_docs, f, indent=4, ensure_ascii=False)

    print(f"Cleaning complete. Processed {len(cleaned_docs)} documents to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
