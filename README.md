# RAG-based Mutual Fund FAQ Chatbot

A production-grade Retrieval-Augmented Generation (RAG) chatbot designed to answer factual questions about mutual fund schemes using official documents from AMCs, SEBI, and AMFI.

## Overview
This chatbot leverages a state-of-the-art RAG pipeline to provide accurate, source-backed information about mutual fund schemes. It specifically targets SBI Mutual Fund schemes, offering details on NAV, expense ratios, exit loads, minimum investments, and regulatory information.

### 📄 Submission Documents
*   **[Source List](source_list.csv)**: Complete list of official URLs for the corpus.
*   **[Sample Q&A](sample_qa.md)**: Example factual questions and answers.
*   **[Disclaimer](#disclaimer)**: Important notice regarding factual limitations.

### AMC Covered
* **SBI Mutual Fund**

### Schemes Covered
* **SBI Large Cap Fund** (formerly known as SBI Bluechip Fund)
* **SBI Small Cap Fund**
* **SBI Focused Fund**
* **SBI Long Term Equity Fund** (ELSS)

---

## Architecture Overview
The chatbot follows a robust RAG architecture:
1.  **Data Ingestion**: Scraped HTML content and parsed PDF documents (Factsheets, KIM, SID) from official sources.
2.  **Cleaning & Chunking**: Cleaned text using regex patterns and applied recursive character splitting with 800-character chunks and 150-character overlap.
3.  **Embeddings**: Generated semantic vectors using the local `all-MiniLM-L6-v2` SentenceTransformers model (384 dimensions).
4.  **Vector Store**: Stored chunks and embeddings in a PostgreSQL database with the `pgvector` extension.
5.  **Retrieval**:
    *   **Semantic Search**: Vector similarity search using the cosine distance operator (`<->`).
    *   **Keyword Fallback**: Literal ILIKE pattern matching for common fund terminology.
    *   **Scheme Filtering**: Strict filtering based on URL patterns (e.g., `sbi-small-cap`, `bluechip`).
6.  **Re-ranking**: Prioritized chunks containing critical technical keywords (NAV, Expense Ratio, Exit Load) and specific factual patterns (e.g., "NAV as on").
7.  **Generation**: Synthesized concise, factual answers using Groq's LLaMA 3.1 8B model, guided by a strict system prompt.

---

## Tech Stack
*   **Backend**: FastAPI (Python)
*   **Frontend**: Streamlit
*   **Database**: PostgreSQL with `pgvector`
*   **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
*   **LLM**: Groq (LLaMA 3.1 8B Instant)
*   **Deployment Tools**: Render (Backend), Vercel (Frontend), GitHub Actions (Scheduler)

---

## Example Queries
*   "What is the NAV of SBI Small Cap Fund?"
*   "What is the exit load for SBI Focused Fund?"
*   "What are the tax benefits of ELSS?"
*   "What is the minimum SIP amount for Large Cap?"
*   "What does the riskometer indicate for Focused Fund?"

---

## Guardrails and Refusal Policy
The system is built with multiple safety layers:
*   **Factual Grounding**: The chatbot only answers if the information exists in the retrieved context. If not, it refuses by saying it doesn't have the factual information.
*   **No Financial Advice**: Detects and refuses investment recommendations ("Should I invest?", "Which is the best fund?").
*   **PII Blocking**: Automatically blocks queries containing sensitive personal information like PAN, Aadhaar, or phone numbers.
*   **AMC Restriction**: Limits responses only to the supported SBI Mutual Fund schemes.
*   **Source Citation**: Every factual answer is mandatory-linked to its official source URL.

---

## Known Limitations
*   **Data Freshness**: The system relies on the latest scraped data. Real-time daily NAVs are retrieved if present in the scraped chunks, otherwise, the system directs the user to the live AMC page.
*   **Scope**: Covers only a selected set of four SBI Mutual Fund schemes.

---

## Setup Instructions

### Prerequisites
*   Python 3.8+
*   PostgreSQL with `pgvector` installed
*   Groq API Key

### Backend Setup
1.  Navigate to the root directory.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables in a `.env` file:
    ```env
    DATABASE_URL=postgresql://user:password@host:port/dbname
    GROQ_API_KEY=your_groq_api_key
    ```
4.  Run the FastAPI server:
    ```bash
    uvicorn Phase_8.api:app --reload
    ```

### Frontend Setup
1.  Run the Streamlit application:
    ```bash
    streamlit run Phase_8/app.py
    ```

---

## Disclaimer
> "This assistant provides factual information about mutual funds based on public documents from AMC, SEBI, and AMFI sources. It does not provide investment advice or recommendations."
