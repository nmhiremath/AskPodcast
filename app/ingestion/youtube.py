"""YouTube caption adapter: raw captions -> list[Segment].

Design: the network call (`fetch_raw_captions`) is separate from the pure
transform (`captions_to_segments`), so the transform is unit-testable offline.
"""
import re

from youtube_transcript_api import YouTubeTranscriptApi

from app.schemas import Segment, Show

# Caption noise like "[Music]" or "[Applause]"
_NOISE = re.compile(r"\[[^\]]*\]")

"""
Sample raw response returned by `fetch_raw_captions(video_id)`:
[
    {
        "text": "Welcome to the Huberman Lab Podcast,",
        "start": 0.0,
        "duration": 2.48
    },
    {
        "text": "where we discuss science and science-based tools",
        "start": 2.48,
        "duration": 2.16
    }
]
"""


def fetch_video_title(video_id: str) -> str:
    """Fetch video title using YouTube's public oEmbed endpoint (no API key needed)."""
    import httpx

    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        resp = httpx.get(url, timeout=5.0)
        if resp.status_code == 200:
            return resp.json().get("title", f"Episode {video_id}")
    except Exception:
        pass
    return f"Episode {video_id}"


def fetch_raw_captions(video_id: str) -> list[dict]:
    """Network call. Returns [{'text': str, 'start': float, 'duration': float}, ...]."""
    return YouTubeTranscriptApi().fetch(video_id, languages=["en"]).to_raw_data()


def captions_to_segments(
    raw: list[dict],
    *,
    show: Show,
    episode_id: str,
    episode_title: str,
    speaker: str,
) -> list[Segment]:
    """Pure transform: clean caption text and wrap each snippet in a Segment."""
    segments: list[Segment] = []
    for cap in raw:
        text = _NOISE.sub("", cap["text"]).replace("\n", " ").strip()
        if not text:  # snippet was only noise like "[Music]"
            continue
        segments.append(
            Segment(
                show=show,
                episode_id=episode_id,
                episode_title=episode_title,
                speaker=speaker,
                start_seconds=cap["start"],
                end_seconds=cap["start"] + cap["duration"],
                text=text,
            )
        )
    return segments
