"""List the Gemini models YOUR API key can actually use, grouped by capability.

Run:  python scripts/list_models.py
"""
import os
import sys

from dotenv import load_dotenv
from google import genai

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    sys.exit("❌ GOOGLE_API_KEY missing in .env")

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

chat, embed = [], []
for m in client.models.list():
    actions = m.supported_actions or []
    if "generateContent" in actions:
        chat.append(m.name)
    if "embedContent" in actions:
        embed.append(m.name)

print("💬 Chat models (generateContent):")
print("\n".join(f"  {n}" for n in sorted(chat)))
print("\n🔢 Embedding models (embedContent):")
print("\n".join(f"  {n}" for n in sorted(embed)))
