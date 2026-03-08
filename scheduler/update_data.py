import os
import hashlib
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Mutual Fund URLs to track
MF_URLS = [
    {"name": "SBI Small Cap Fund", "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-small-cap-fund-329"},
    {"name": "SBI Focused Fund", "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-focused-fund-25"},
    {"name": "SBI Long Term Equity Fund", "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-long-term-equity-fund-(previously-known-as-sbi-magnum-taxgain-scheme)-3"},
    {"name": "General - AMFI", "url": "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=expenseRatio"}
]

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def setup_metadata_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fund_metadata (
            fund_name TEXT PRIMARY KEY,
            source_url TEXT,
            content_hash TEXT,
            last_updated TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def generate_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def run_refresh_pipeline():
    print("Starting mutual fund refresh pipeline...")
    
    setup_metadata_table()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    processed = 0
    updated = 0
    skipped = 0
    
    for mf in MF_URLS:
        processed += 1
        name = mf["name"]
        url = mf["url"]
        
        # Get existing hash
        cur.execute("SELECT content_hash FROM fund_metadata WHERE fund_name = %s", (name,))
        row = cur.fetchone()
        existing_hash = row[0] if row else None
        
        content = fetch_page_content(url)
        if content is None:
            skipped += 1
            continue
            
        new_hash = generate_hash(content)
        
        if existing_hash == new_hash:
            print(f"Skipping unchanged fund: {name}")
            skipped += 1
        else:
            print(f"Updating metadata for: {name}")
            cur.execute("""
                INSERT INTO fund_metadata (fund_name, source_url, content_hash, last_updated)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (fund_name) DO UPDATE 
                SET content_hash = EXCLUDED.content_hash, 
                    last_updated = EXCLUDED.last_updated
            """, (name, url, new_hash, datetime.now()))
            updated += 1
            
    conn.commit()
    cur.close()
    conn.close()
    
    print("\nUpdate Summary")
    print(f"Funds processed: {processed}")
    print(f"Funds updated: {updated}")
    print(f"Funds skipped: {skipped}")
    print("Database updated successfully")

if __name__ == "__main__":
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment variables.")
    else:
        run_refresh_pipeline()
