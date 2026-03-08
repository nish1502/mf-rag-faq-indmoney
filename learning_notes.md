# Learning Notes – RAG-based Mutual Fund FAQ Chatbot

## Key Concepts Learned

### 1. Retrieval-Augmented Generation (RAG)
I learned how RAG systems combine:
- vector search
- document retrieval
- LLM generation

This ensures answers are grounded in real documents instead of hallucinated by the model.

---

### 2. Vector Databases
Using **pgvector with PostgreSQL**, I stored embeddings of mutual fund documents and retrieved relevant chunks using similarity search.

---

### 3. Embeddings
Semantic embeddings were generated using the **SentenceTransformers all-MiniLM-L6-v2 model**, allowing the chatbot to match user queries with relevant context.

---

### 4. Guardrails
The system includes safety mechanisms such as:
- blocking investment advice
- refusing queries containing personal information (PAN, Aadhaar)
- limiting responses only to supported schemes

---

### 5. Deployment Challenges
Deploying ML-based systems on free hosting tiers introduces constraints such as:
- memory limits
- cold start delays

To address this, the production deployment was optimized to reduce heavy model loading.

---

## Key Takeaways
- RAG pipelines help build reliable AI systems grounded in verified data.
- Vector search significantly improves information retrieval for domain-specific assistants.
- Production deployment requires optimizing memory usage and startup time.

---

## Future Improvements
- Add support for more AMCs and schemes
- Implement caching for faster responses
- Add user authentication and conversation history