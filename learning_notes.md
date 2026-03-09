# Learning Notes – Building a Production RAG System for Mutual Fund FAQs

## Project Context

As part of the NextLeap AI Bootcamp, I built a **RAG-based Mutual Fund FAQ Assistant** designed to answer factual questions about mutual fund schemes using **verified AMC, SEBI, and AMFI documents**.

The goal was to simulate how a **fintech platform could automate repetitive mutual fund support queries** while ensuring that responses remain:

- factually grounded  
- source-cited  
- compliant with financial advisory regulations  

Unlike a simple chatbot, the system needed to enforce **strict factual guardrails**, refuse opinion-based questions, and always link answers to **official documents**.

---

## System Design Overview

High-level flow of the RAG pipeline:

User Query  
↓  
Query Normalization  
↓  
Embedding Generation  
↓  
Vector Similarity Search (PostgreSQL + pgvector)  
↓  
Context Retrieval & Re-ranking  
↓  
LLM Generation (Groq LLaMA 3.1)  
↓  
Final Answer + Source Citation

This architecture ensures the LLM only generates responses grounded in retrieved documents from verified AMC, SEBI, and AMFI sources.

---

# Major Technical Challenges and How They Were Solved

Building the system involved multiple engineering and deployment issues.

---

# 1. Embedding API Failures

Initially the system used an **external embedding API**.

Problems encountered:

- API quota limits  
- request failures  
- inconsistent latency  

### Solution

The system was refactored to use **local embeddings with SentenceTransformers (all-MiniLM-L6-v2)**.

Benefits:

- predictable performance  
- no dependency on external APIs  
- faster experimentation during development  

Later during deployment the system was optimized to optionally use **external embedding generation** to reduce memory usage on Render.

---

# 2. Vector Database Schema Issues

During retrieval testing the database query failed with the error:

```
column "scheme" does not exist
```

### Root Cause

The database stored **URL-based references** for schemes but the retrieval logic expected a `scheme` column.

### Solution

A **scheme-to-URL mapping layer** was implemented.

Example mapping:

```
"SBI Small Cap Fund" → small-cap
"SBI Focused Fund" → focused
"SBI Long Term Equity Fund" → long-term
"SBI Large Cap Fund" → large-cap
```

Retrieval queries were updated to filter using **URL pattern matching**.

---

# 3. Scheme Filtering Breaking Retrieval

After introducing scheme filtering, the chatbot returned **no results for some schemes**, particularly **SBI Large Cap Fund**.

### Root Cause

AMC URLs used **legacy naming conventions**.

Example:

```
sbi-large-cap-fund
sbi-bluechip-fund
```

### Solution

The retrieval logic was expanded to support **multiple URL patterns**.

```
large-cap OR bluechip
```

This restored retrieval accuracy.

---

# 4. Missing Corpus Data

When querying:

```
What is the NAV of SBI Large Cap Fund?
```

The system returned:

```
I do not have the factual information for this request.
```

### Root Cause

Large Cap scheme documents were **not included in the ingestion pipeline**.

### Solution

The ingestion pipeline was expanded to include:

- AMC scheme page  
- Factsheets  
- KIM documents  
- SID documents  

This added **~489 additional document chunks** to the vector database.

---

# 5. Query Normalization Challenges

User queries varied widely:

```
NAV of fund
fund nav
net asset value
```

Without normalization the retrieval pipeline sometimes missed relevant chunks.

### Solution

A **query normalization dictionary** was implemented.

Examples:

```
"net asset value" → "nav"
"fund nav" → "nav"
"tax benefits" → "section 80c"
```

This significantly improved retrieval consistency.

---

# 6. ELSS Tax Benefit Edge Case

Evaluation tests required that ELSS answers mention the **mandatory lock-in period**.

Some retrieved chunks mentioned **Section 80C** but not the lock-in period.

### Solution

A **context enrichment rule** was added.

If a query contains:

```
ELSS
section 80c
tax benefits
```

Inject the statement:

```
ELSS schemes have a statutory lock-in period of 3 years from the date of allotment.
```

This ensured correct responses while avoiding hallucination.

---

# 7. Deployment Challenges on Render

Deployment introduced several constraints.

### Problem 1 – Memory limitations

Loading SentenceTransformers models increased startup time and memory usage.

### Problem 2 – Cold start latency

Render free-tier instances sleep when inactive.

### Solution

The backend was optimized to:

- reduce heavy ML dependencies  
- lazy-load models  
- rely primarily on vector database retrieval  

Cold start behavior was documented in the README.

---

# 8. FastAPI Endpoint Hanging

During production testing the `/chat` endpoint appeared to hang with no logs.

### Solution

Several debugging tools were added:

- request logging middleware  
- diagnostic `/test` endpoint  
- detailed retrieval logging  

This helped isolate issues in the retrieval pipeline.

---

# 9. Metadata Synchronization Bug

The UI displays:

```
Last updated: <date>
```

However it remained stuck at:

```
05-03-2026
```

even after the scheduler ran successfully.

### Root Cause

The `/metadata` endpoint returned a **static variable** rather than a dynamic timestamp.

### Solution

The endpoint was updated to generate timestamps dynamically:

```
datetime.now().strftime("%d %B %Y, %I:%M %p")
```

This synchronized backend updates with the frontend UI.

---

# Key Engineering Lessons

## Observability is critical in production AI systems

Debugging distributed pipelines requires:

- structured logging  
- diagnostic endpoints  
- monitoring  

Without observability, identifying failures becomes extremely difficult.

---

## Data quality matters more than model size

Most improvements came from:

- improving document ingestion  
- normalizing queries  
- refining retrieval logic  

rather than changing the LLM itself.

---

## Retrieval design is the core of RAG systems

Key retrieval improvements included:

- query normalization  
- scheme filtering  
- keyword fallback search  
- context re-ranking  

---

# AI Product Management Perspective

From a product perspective, the assistant was designed around **user trust and regulatory safety**.

## Product Design Principles

### 1. Facts-only responses

Financial applications must avoid unauthorized investment advice.

### 2. Mandatory source citations

Every answer links to official documents.

### 3. Short responses

Answers are limited to **three sentences** to reduce hallucination risk.

### 4. Explicit refusal policy

The assistant refuses questions such as:

```
Should I invest in this fund?
Which fund is the best?
```

---

# Target Product Use Cases

Potential real-world applications include:

- fintech customer support assistants  
- investment research assistants  
- educational tools for retail investors  
- AMC FAQ automation systems  

---

## AI System Metrics (Future)

If deployed in production, the following metrics would be important to monitor:

- **Query Success Rate** – percentage of queries answered with verified context.
- **Retrieval Accuracy** – how often the correct document chunk is retrieved.
- **Refusal Accuracy** – ability to correctly reject opinion-based questions.
- **Average Response Latency** – time taken to return an answer.
- **Citation Reliability** – percentage of answers that include valid official sources.

Monitoring these metrics would help continuously improve both the retrieval pipeline and user experience.

---
# Future Product Improvements

Potential roadmap features:

- multi-AMC coverage  
- multilingual support for Indian investors  
- real-time NAV refresh pipelines  
- conversational memory  
- portfolio analytics integration  

---

# If I Built This Inside a Fintech Startup

If this system were deployed inside a production fintech environment, I would focus on the following improvements.

## Real-time data pipelines

Implement automated pipelines that refresh NAV and scheme data daily using **AMFI feeds or AMC APIs**.

---

## Monitoring and evaluation dashboards

Track system metrics such as:

- retrieval accuracy  
- hallucination rate  
- refusal accuracy  
- response latency  

---

## Hybrid retrieval architecture

Combine:

- vector search  
- structured financial data  
- curated FAQs  

to improve reliability.

---

## Compliance safeguards

Integrate compliance rules to ensure responses remain within regulatory boundaries for financial advice.

---

## Personalization layer

Allow users to:

- compare mutual funds  
- analyze portfolio exposure  
- receive educational explanations for financial terms  

---

# What This Project Demonstrates About My AI PM Skills

This project reflects several core AI Product Management capabilities.

## Problem framing

Identifying a **real fintech user problem**: accessing reliable mutual fund information quickly.

## Product safety design

Designing guardrails to prevent:

- financial advice generation  
- personal data usage  
- hallucinated financial facts  

## AI system thinking

Understanding how **retrieval systems, LLMs, and product UX interact**.

## Iterative development

Debugging multiple production issues across:

- data ingestion  
- retrieval pipelines  
- deployment infrastructure  

---

# Final Reflection

Building this project demonstrated that successful AI applications require far more than connecting an LLM to an interface.

Production AI systems require expertise in:

- data engineering  
- retrieval system design  
- prompt engineering  
- deployment optimization  
- product-level safety constraints  

This project helped me understand how **AI systems move from prototypes to reliable real-world applications**, particularly in highly regulated domains like finance.