"""Ingestion package: adapters and transcript chunking."""
from app.ingestion.chunking import chunk_segments
from app.ingestion.youtube import (
    captions_to_segments,
    extract_video_id,
    fetch_raw_captions,
    fetch_video_title,
)

__all__ = [
    "captions_to_segments",
    "chunk_segments",
    "extract_video_id",
    "fetch_raw_captions",
    "fetch_video_title",
]
