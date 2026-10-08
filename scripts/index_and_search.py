"""Index a cached podcast episode into ChromaDB and run a test query.

Run:  python -m scripts.index_and_search QmOF0crdyRU "What causes a dopamine crash?"
"""

import json
import sys
from pathlib import Path

from app.ingestion import captions_to_segments, chunk_segments
from app.vectorstore import get_vectorstore, index_chunks, similarity_search_with_scores

if len(sys.argv) < 2:
    sys.exit("Usage: python -m scripts.index_and_search <video_id> [query]")

video_id = sys.argv[1]
query = sys.argv[2] if len(sys.argv) > 2 else "How does dopamine affect motivation and craving?"

cache_file = Path("data/raw/huberman_lab") / f"{video_id}.json"
if not cache_file.exists():
    sys.exit(f"❌ Cache file not found: {cache_file}. Run `python -m scripts.fetch_episode {video_id}` first.")

# 1. Load cached transcript
payload = json.loads(cache_file.read_text())
title = payload["title"]
captions = payload["captions"]
print(f"📖 Loaded '{title}' ({len(captions)} caption snippets)")

# 2. Convert to Segments and Chunks
segments = captions_to_segments(
    captions,
    show=payload["show"],
    episode_id=video_id,
    episode_title=title,
    speaker=payload["speaker"],
)
chunks = chunk_segments(segments, target_words=200, overlap_words=40)
print(f"🧩 Generated {len(chunks)} chunks")

# 3. Index into ChromaDB
print("🚀 Indexing chunks into ChromaDB (embedding via Gemini)...")
vs = get_vectorstore()
count = index_chunks(chunks, vectorstore=vs)
print(f"✅ Indexed {count} chunks into ChromaDB!\n")

# 4. Perform test retrieval
print(f"🔍 Searching for query: {query!r}")
results = similarity_search_with_scores(query, k=3, vectorstore=vs)

print(f"\nTop {len(results)} Retrieved Results:")
for rank, (doc, score) in enumerate(results, start=1):
    meta = doc.metadata
    print(f"\n[{rank}] Score: {score:.4f} | Timestamp: [{meta['timestamp']}] ({meta['start_seconds']}s)")
    print(f"    Episode: {meta['episode_title']}")
    print(f"    Excerpt: {doc.page_content[:250]}...")
