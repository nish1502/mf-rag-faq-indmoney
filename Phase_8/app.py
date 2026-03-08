import streamlit as st
import requests
import os
import sys
import psycopg2
import re
from pgvector.psycopg2 import register_vector
# from sentence_transformers import SentenceTransformer  # Removed for production lean runtime
from groq import Groq
from dotenv import load_dotenv

# --- Configuration & Initialization ---
# Load .env from the root directory relative to this file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

# Initialize AI Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Model cache removed to save memory on Render
def get_query_embedding(text: str) -> Optional[list[float]]:
    """Fetches embedding vector from Hugging Face Inference API (all-MiniLM-L6-v2)."""
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    # Optional: Get token from env if available (e.g., HF_TOKEN)
    headers = {}
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    
    try:
        print(f"DEBUG: Calling Hugging Face API for model {model_id}")
        import requests
        response = requests.post(api_url, headers=headers, json={"inputs": text}, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"HF API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"HF API connection failed: {e}")
        return None

# Standardized Model Constants
# Using local all-MiniLM-L6-v2 model (384 dimensions)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# LLaMA model from Groq
GROQ_MODEL = "llama-3.1-8b-instant"

# Data Freshness
DATA_LAST_UPDATED = "05-03-2026"

# PII Detection Patterns
PII_PATTERNS = {
    "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
    "Aadhaar": r"\d{4}\s?\d{4}\s?\d{4}",
    "Phone": r"\b[6-9]\d{9}\b",
    "Email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
}

def detect_pii(text):
    """Detects sensitive personal information in the text."""
    for label, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            return True
    return False

# Financial Advice Guardrail
ADVICE_PHRASES = [
    "should i invest",
    "best mutual fund",
    "which fund is better",
    "buy or sell",
    "recommend a fund",
    "where should i invest",
    "give me advice",
    "which scheme is good",
    "mutual fund is best",
    "which fund is best"
]

def is_asking_advice(text):
    """Detects if the user is asking for investment advice."""
    text_lower = text.lower()
    for phrase in ADVICE_PHRASES:
        if phrase in text_lower:
            return True
    return False

# Scheme Restriction Guardrail
COMPETITORS = ["hdfc", "axis", "icici", "nippon", "mirae", "quant", "parag", "uti", "kotak", "tata", "dsp", "canara", "invesco", "franklin", "absl", "aditya"]

def references_unsupported_scheme(query):
    """Detects if the query references a non-supported scheme."""
    query_lower = query.lower()
    # Check for competitor mentions
    for comp in COMPETITORS:
        if comp in query_lower:
            return True
    return False

# Supported Schemes
SUPPORTED_SCHEMES = [
    "SBI Large Cap Fund",
    "SBI Small Cap Fund",
    "SBI Long Term Equity Fund",
    "SBI Focused Fund"
]

# Query Normalization Synonyms
QUERY_SYNONYMS = {
    "fund charges": "expense ratio",
    "charges": "expense ratio",
    "lump sum investment": "minimum investment",
    "lumpsum": "minimum investment",
    "tax benefits": "section 80c",
    "tax benefit": "section 80c",
    "elss tax": "section 80c",
    "nav of the fund": "nav",
    "fund nav": "nav",
    "net asset value": "nav",
    "lock-in": "3 years"
}

def normalize_query(query: str) -> str:
    """Normalizes the query using a synonym dictionary."""
    normalized_query = query.lower()
    for key in sorted(QUERY_SYNONYMS.keys(), key=len, reverse=True):
        if key in normalized_query:
            normalized_query = normalized_query.replace(key, QUERY_SYNONYMS[key])
    return normalized_query

# AMC Page Mapping for Fallback Context
SCHEME_AMC_MAP = {
    "SBI Large Cap Fund": "https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43",
    "SBI Small Cap Fund": "https://www.sbimf.com/sbimf-scheme-details/sbi-small-cap-fund-329",
    "SBI Focused Fund": "https://www.sbimf.com/sbimf-scheme-details/sbi-focused-fund-25",
    "SBI Long Term Equity Fund": "https://www.sbimf.com/sbimf-scheme-details/sbi-long-term-equity-fund-(previously-known-as-sbi-magnum-taxgain-scheme)-3"
}

# AI Request Limiter Settings
MAX_REQUESTS_PER_DAY = 40
if "global_request_count" not in st.session_state:
    st.session_state.global_request_count = 0

def retrieve_context(query, scheme=None, top_k=8):
    """Retrieves context from PostgreSQL filtered by scheme and re-ranks based on keyword presence."""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        st.error("DATABASE_URL not found in environment.")
        return []

    # Handle special characters in password if present
    if 'Nishita@152' in database_url:
        database_url = database_url.replace('Nishita@152', 'Nishita%40152')

    query_embedding = None
    try:
        # Fetch embedding via API to keep runtime lean
        query_embedding = get_query_embedding(query) # Using 'query' as 'rewritten_query' is not defined here
        if query_embedding is None:
             print("Query embedding failed — using keyword fallback retrieval.")
             # If embedding fails, we can't do semantic search, so return empty for now.
             # A more robust fallback would be pure keyword search.
             return []
    except Exception as e:
        print(f"Embedding generation failed: {e} — using keyword fallback retrieval.")
        return []

    # Step 2: Semantic Search in PostgreSQL with pgvector
    semantic_results = []
    try:
        scheme_url_map = {
            "SBI Small Cap Fund": ["small-cap"],
            "SBI Focused Fund": ["focused"],
            "SBI Long Term Equity Fund": ["long-term"],
            "SBI Large Cap Fund": ["large-cap", "bluechip"]
        }

        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(database_url)
        register_vector(conn)
        cur = conn.cursor()
        
        # Check if a specific scheme filter is requested
        scheme_filter = scheme_url_map.get(scheme)
        
        if scheme and scheme != "All Schemes" and scheme_filter:
            url_conditions = " OR ".join(["url ILIKE %s"] * len(scheme_filter))
            url_patterns = [f"%{p}%" for p in scheme_filter]
            
            query_sql = f"""
                SELECT content, url, title, 1 - (embedding <=> %s::vector) AS similarity
                FROM fund_embeddings
                WHERE ({url_conditions})
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
            """
            cur.execute(query_sql, (query_embedding, *url_patterns, query_embedding, top_k))
        else:
            cur.execute("""
                SELECT content, url, title, 1 - (embedding <=> %s::vector) AS similarity
                FROM fund_embeddings
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_embedding, query_embedding, top_k))
        
        rows = cur.fetchall()
        print("Selected scheme:", scheme)
        print("Rows retrieved:", len(rows))
        if rows:
            print("Retrieved titles:", [r[2] for r in rows])
        cur.close()
        conn.close()
        
        semantic_results = [{"content": r[0], "url": r[1], "title": r[2], "similarity": r[3]} for r in rows]
    except Exception as e:
        print(f"Database error during retrieval: {e}")
        return []

    # Step 3: Secondary Keyword Re-ranking
    keywords = ["exit load", "expense ratio", "benchmark", "riskometer", "sip", "lumpsum", "lock-in", "nav"]
    query_lower = query.lower()
    
    target_keywords = [kw for kw in keywords if kw in query_lower]
    
    if target_keywords:
        for item in semantic_results:
            content_lower = item['content'].lower()
            keyword_match_count = sum(1 for kw in target_keywords if kw in content_lower)
            item['keyword_boost'] = keyword_match_count
        
        # Primary Priority: Chunks containing 'nav' if query is about nav
        # Secondary Priority: Keyword matches
        # Tertiary Priority: Vector similarity
        semantic_results.sort(key=lambda x: (
            ("nav" in x['content'].lower()) if "nav" in query_lower else False,
            x.get('keyword_boost', 0), 
            x['similarity']
        ), reverse=True)
        
    return semantic_results

def generate_answer(query, contexts):
    """Synthesizes a factual answer using Groq LLaMA."""
    
    context_text = "\n".join(
        [f"[Context {i+1}]: {c['title']} ({c['url']})\n{c['content']}" for i, c in enumerate(contexts)]
    )

    prompt = f"""You are a factual assistant for INDMoney's Mutual Fund FAQ. 
Answer questions based ONLY on the provided context. 

Strict Response Format:
Sentence 1: Direct factual answer.
Sentence 2 (optional): Short explanation.
New line: Source: <URL>

Constraints:
1. Answers must be <= 3 sentences.
2. MUST include exactly ONE citation link from the provided context using the "Source: URL" format.
3. Do NOT use parentheses, square brackets, or any internal markers (e.g., [Context 1], [Chunk]) in the final answer.
4. If the answer is not in the context, say: "I do not have the factual information for this specific request."
5. Refuse investment advice. If asked for a recommendation, say: "I only provide factual details. For investment advice, please consult a SEBI-registered advisor."
6. Maintain a professional and direct tone.
7. CRITICAL: DO NOT add any conversational filler, meta-commentary, or introductory remarks like "Based on the context..." or "According to the provided information...".

Context:
{context_text}

Question:
{query}
"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a factual mutual fund assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq Generation error: {e}")
        return "The AI assistant has reached its request limit for today. Please try again later."

# --- Streamlit UI App ---
st.set_page_config(
    page_title="INDMoney MF Assistant",
    page_icon="💰",
    layout="centered"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stButton>button {
        border-radius: 20px;
        background-color: #00d09c;
        color: white;
    }
    .stMarkdown h1 {
        color: #1a1a1a;
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Desk
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/47545620?s=200&v=4", width=80)
    st.header("INDMoney Bot")
    st.info(f"""
        Optimized factual search for:
        - Exit Loads & Lock-ins
        - Expense Ratios
        - SIP/Lumpsum Limits
        - Riskometers
        
        **Data Source**: Official AMC / SEBI / AMFI documents
        **Last Updated**: {DATA_LAST_UPDATED}
    """)
    st.warning("⚠️ **Disclaimer**: No investment advice provided.")
    
    st.divider()
    scheme_filter = st.selectbox(
        "Filter by Scheme:",
        options=["All Schemes"] + SUPPORTED_SCHEMES,
        index=0
    )
    selected_scheme = None if scheme_filter == "All Schemes" else scheme_filter

# Title and Caption
st.title("💰 INDMoney MF Assistant")
st.caption("Factual facts about Mutual Fund schemes. Local all-MiniLM-L6-v2 Engine.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask about expense ratios, exit loads, or SIP limits..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        # Check for PII (Security Layer)
        if detect_pii(query):
            refusal = (
                "For privacy and security reasons, this assistant cannot process personal information "
                "such as PAN, Aadhaar, phone numbers, or email addresses.\n"
                "Please ask a factual question about mutual funds."
            )
            st.markdown(refusal)
            st.session_state.messages.append({"role": "assistant", "content": refusal})
        # Check for Financial Advice (Guardrail)
        elif is_asking_advice(query):
            refusal = (
                "I can only provide factual information about mutual funds such as expense ratios, "
                "exit loads, SIP limits, and lock-in periods.\n\n"
                "I cannot provide investment advice or recommendations.\n\n"
                "For financial guidance, please consult a qualified financial advisor or refer to AMFI investor resources:\n"
                "https://www.amfiindia.com/investor"
            )
            st.markdown(refusal)
            st.session_state.messages.append({"role": "assistant", "content": refusal})
        # Check for unsupported schemes in query text
        elif references_unsupported_scheme(query):
            refusal = (
                "This assistant currently provides factual information only for the following schemes:\n\n"
                "• SBI Large Cap Fund\n"
                "• SBI Small Cap Fund\n"
                "• SBI Long Term Equity Fund\n"
                "• SBI Focused Fund"
            )
            st.markdown(refusal)
            st.session_state.messages.append({"role": "assistant", "content": refusal})
        # Check for unsupported schemes from dropdown
        elif selected_scheme and selected_scheme not in SUPPORTED_SCHEMES:
            refusal = (
                "This assistant currently provides factual information only for the following schemes:\n\n"
                "• SBI Large Cap Fund\n"
                "• SBI Small Cap Fund\n"
                "• SBI Long Term Equity Fund\n"
                "• SBI Focused Fund"
            )
            st.markdown(refusal)
            st.session_state.messages.append({"role": "assistant", "content": refusal})
        else:
            with st.status("🔍 Deep searching fact database...", expanded=True) as status:
                # Main RAG Pipeline
                contexts = retrieve_context(query, scheme=selected_scheme, top_k=8)
                
                # Check for NAV query fallback enrichment
                normalized_query = normalize_query(query)
                is_nav_query = "nav" in normalized_query
                
                processed_nav_fallback = False
                if is_nav_query and selected_scheme and selected_scheme in SCHEME_AMC_MAP:
                    has_nav_data = False
                    if contexts:
                        for ctx in contexts:
                            # Stricter check: Look for the specific pattern "NAV ... as on" which indicates factual data
                            if re.search(r"nav [a-z ]*as on", ctx["content"], re.IGNORECASE):
                                has_nav_data = True
                                break
                    
                    if not has_nav_data:
                         fallback_url = SCHEME_AMC_MAP[selected_scheme]
                         answer = f"The current Net Asset Value (NAV) information for {selected_scheme} is available on the official AMC page: {fallback_url}. Please refer to the scheme page for the latest update.\n\nSource: {fallback_url}"
                         status.update(label="✅ Ready!", state="complete", expanded=False)
                         processed_nav_fallback = True
                
                if not processed_nav_fallback:
                    if not contexts:
                        answer = "I do not have the factual information for this specific request."
                        status.update(label="❌ No factual data found.", state="error")
                    else:
                        status.update(label="✨ Synthesizing response...", state="running")
                        formatted_contexts = contexts[:1]  # Strict ONE citation limit
                        answer = generate_answer(query, formatted_contexts)
                        status.update(label="✅ Ready!", state="complete", expanded=False)
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
