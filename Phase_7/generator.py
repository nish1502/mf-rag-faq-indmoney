from groq import Groq
from dotenv import load_dotenv

# System Prompt to enforce the 'Senior AI Architect' persona and product constraints
SYSTEM_PROMPT = """
You are a factual assistant for INDMoney's Mutual Fund FAQ. 
Answer questions based ONLY on the provided context. 

Constraints:
1. Answers must be <= 3 sentences.
2. MUST include exactly ONE citation link from the provided context.
3. If the answer is not in the context, say: "I do not have the factual information for this specific request."
4. Refuse investment advice. If asked for a recommendation or performance comparison, say: "I only provide factual details. For investment advice, please consult a SEBI-registered advisor."
5. No PII allowed.
6. Tone: Professional and direct.
"""

def generate_answer(query, contexts):
    """Generates an answer using Groq LLaMA."""
    load_dotenv(dotenv_path="../.env")
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("Error: Missing GROQ_API_KEY.")
        return "API Key missing."

    client = Groq(api_key=api_key)
    
    # Format context for the LLM
    context_text = ""
    for idx, ctx in enumerate(contexts):
        context_text += f"\n[Context {idx+1}]: {ctx['title']} ({ctx['url']})\n{ctx['content']}\n"

    prompt = f"User Question: {query}\n\nSearch Context:\n{context_text}"

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "An error occurred during generation."


if __name__ == "__main__":
    # Test case with mock context
    mock_query = "What is the exit load for SBI Small Cap Fund?"
    mock_contexts = [
        {
            "title": "SBI Small Cap Fund Details",
            "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-small-cap-fund-329",
            "content": "Exit Load: For exit within 1 year from the date of allotment - 1%; For exit after 1 year from the date of allotment - Nil."
        }
    ]
    
    print(f"Testing generation for: '{mock_query}'")
    answer = generate_answer(mock_query, mock_contexts)
    print(f"\nResponse:\n{answer}")
