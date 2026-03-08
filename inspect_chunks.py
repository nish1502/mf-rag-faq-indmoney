import os
import sys

sys.path.append(os.getcwd())

from Phase_8.api import retrieve_context
from dotenv import load_dotenv

load_dotenv()

res = retrieve_context("What are the tax benefits of ELSS?")

for i, r in enumerate(res):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Title: {r['title']}")
    print(f"Similarity: {r['similarity']:.4f}")
    print("Contains NAV:", "nav" in r["content"].lower())
    print(r["content"][:200])