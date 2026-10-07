"""Fetch one YouTube episode and preview its Segments.

Run (from project root):  python -m scripts.fetch_episode <video_id>
"""
import json
from pathlib import Path
import sys

from app.ingestion import captions_to_segments, chunk_segments, fetch_raw_captions, fetch_video_title

video_id = sys.argv[1]

show = "huberman_lab"
speaker = "Andrew Huberman"

# 1. Cache raw captions under data/raw/{show}/{video_id}.json
cache_dir = Path("data/raw") / show
cache_dir.mkdir(parents=True, exist_ok=True)
cache_file = cache_dir / f"{video_id}.json"

if cache_file.exists():
    print(f"📦 Loading cached episode from {cache_file}...")
    cached_payload = json.loads(cache_file.read_text())
    title = cached_payload["title"]
    raw = cached_payload["captions"]
else:
    print(f"🌐 Fetching live captions and title for {video_id}...")
    title = fetch_video_title(video_id)
    raw = fetch_raw_captions(video_id)
    payload = {
        "show": show,
        "episode_id": video_id,
        "title": title,
        "speaker": speaker,
        "captions": raw,
    }
    cache_file.write_text(json.dumps(payload, indent=2))
    print(f"💾 Saved episode to {cache_file}")

print(f"🎬 Title: '{title}'")

# 3. Build Segments
segments = captions_to_segments(
    raw,
    show="huberman_lab",
    episode_id=video_id,
    episode_title=title,
    speaker="Andrew Huberman",
)
print(f"✅ Parsed {len(segments)} segments")

# 4. Chunk into retrieval-sized blocks
chunks = chunk_segments(segments, target_words=200, overlap_words=40)
print(f"🧩 Created {len(chunks)} chunks (avg ~200 words each)\n")

print("--- Previewing Chunk #0 ---")
c0 = chunks[0]
print(f"ID:        {c0.chunk_id}")
print(f"Timestamp: [{c0.timestamp}] ({c0.start_seconds:.1f}s -> {c0.end_seconds:.1f}s)")
print(f"Text:      {c0.text[:200]}...")
