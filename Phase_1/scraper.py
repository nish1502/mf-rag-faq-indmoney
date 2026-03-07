import asyncio
import json
import os
import io
import requests
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pypdf import PdfReader

# Configuration
URLS_FILE = "urls.txt"
OUTPUT_FILE = "raw_documents.json"
CONCURRENCY_LIMIT = 3  # Number of pages to process at once

async def scrape_html(page, url):
    """Scrapes content from HTML pages using Playwright."""
    try:
        print(f"Scraping HTML: {url}")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Get page title
        title = await page.title()
        
        # Get body inner text (often cleaner than HTML)
        content = await page.evaluate("() => document.body.innerText")
        
        # Use BeautifulSoup to refine cleaning if needed (remove script/style)
        html_content = await page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()
        
        clean_content = soup.get_text(separator="\n", strip=True)
        
        return {
            "url": url,
            "title": title or "Untitled",
            "content": clean_content
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_pdf(url):
    """Downloads and extracts text from PDF files."""
    try:
        print(f"Processing PDF: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with io.BytesIO(response.content) as f:
            reader = PdfReader(f)
            title = os.path.basename(url)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        return {
            "url": url,
            "title": title,
            "content": text.strip()
        }
    except Exception as e:
        print(f"Error processing PDF {url}: {e}")
        return None

async def process_url(url, browser_context, semaphore):
    async with semaphore:
        if url.lower().endswith(".pdf"):
            # PDFs are handled outside Playwright for better text extraction
            return scrape_pdf(url)
        else:
            page = await browser_context.new_page()
            result = await scrape_html(page, url)
            await page.close()
            return result

async def main():
    if not os.path.exists(URLS_FILE):
        print(f"Error: {URLS_FILE} not found.")
        return

    with open(URLS_FILE, "r") as f:
        # Strip whitespace and trailing dots from URLs
        urls = [line.strip().rstrip('.') for line in f if line.strip()]

    print(f"Starting scraper for {len(urls)} URLs...")
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        tasks = [process_url(url, context, semaphore) for url in urls]
        items = await asyncio.gather(*tasks)
        
        results = [item for item in items if item is not None]
        
        await browser.close()

    # Save results to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"Scraping complete. Saved {len(results)} documents to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
