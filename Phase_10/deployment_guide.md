# Deployment Guide - INDMoney MF FAQ Chatbot

### Backend: Streamlit (Streamlit Cloud or Render)
1. Push your code to a GitHub repository.
2. In [Streamlit Cloud](https://streamlit.io/cloud), connect your repo.
3. Set the **Main file path** to `Phase_8/app.py`.
4. Add the following **Secrets** in the Streamlit Cloud Dashboard:
   - `GROQ_API_KEY`: Your Groq API Key.
   - `DATABASE_URL`: Your PostgreSQL (pgvector) connection string.

### Database: Supabase/Neon (PostgreSQL + pgvector)
1. Enable the `pgvector` extension: `CREATE EXTENSION IF NOT EXISTS vector;`
2. Ensure the `fund_embeddings` table is created (Phase 5 takes care of this).

### Frontend: Vercel (Optional Landing Page)
1. Deploy the `Phase_9` content to Vercel as a static site.
2. If you've built a React/Next.js frontend, configure your API endpoint to point to the Streamlit app's URL.

### Update Scheduler: GitHub Actions (Phase 12)
1. Add `GROQ_API_KEY` and `DATABASE_URL` to your GitHub repository's **Secrets (Settings > Secrets and variables > Actions)**.
2. The workflow will automatically run every Sunday at midnight (UTC).
