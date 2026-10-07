"""Step 1 smoke test: confirm we can reach Gemini for BOTH chat and embeddings.

Run:  python scripts/smoke_test_gemini.py
"""
import os
import sys

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()  # reads .env into os.environ

if not os.getenv("GOOGLE_API_KEY"):
    sys.exit("❌ GOOGLE_API_KEY missing. Copy .env.example -> .env and add your key.")

chat_model = os.environ["CHAT_MODEL"]        # fail loudly if unset: no stale defaults
embed_model = os.environ["EMBEDDING_MODEL"]

# 1) Generation: the "G" in RAG
# max_retries=1: a 404 (bad model ID) will never succeed on retry, so fail fast.
llm = ChatGoogleGenerativeAI(model=chat_model, temperature=0, max_retries=1)
reply = llm.invoke("Reply with exactly: PONG")
print(f"✅ Chat  [{chat_model}] -> {reply.text!r}")  # .text flattens content blocks

# 2) Embeddings: the "R" in RAG (what ChromaDB will store)
embedder = GoogleGenerativeAIEmbeddings(model=embed_model)
vector = embedder.embed_query("Huberman on dopamine and motivation")
print(f"✅ Embed [{embed_model}] -> dim={len(vector)}, first3={vector[:3]}")
