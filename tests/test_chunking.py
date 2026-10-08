from app.ingestion import chunk_segments
from app.schemas import Segment

BASE_META = dict(
    show="huberman_lab",
    episode_id="ep-101",
    episode_title="Dopamine Basics",
    speaker="Andrew Huberman",
)


def _make_seg(text: str, start: float, end: float, speaker: str = "Andrew Huberman") -> Segment:
    return Segment(
        show="huberman_lab",
        episode_id="ep-101",
        episode_title="Dopamine Basics",
        speaker=speaker,
        text=text,
        start_seconds=start,
        end_seconds=end,
    )


def test_chunking_preserves_timestamp_boundaries():
    # 3 short segments
    segments = [
        _make_seg("Dopamine is a key neuromodulator in the brain.", 10.0, 15.0),
        _make_seg("It drives motivation, craving, and pursuit of goals.", 15.0, 22.0),
        _make_seg("When dopamine drops, motivation drops immediately.", 22.0, 28.0),
    ]
    # Target 10 words so they pack into a chunk
    chunks = chunk_segments(segments, target_words=100, overlap_words=10)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.start_seconds == 10.0
    assert chunk.end_seconds == 28.0
    assert chunk.timestamp == "00:00:10"
    assert "Dopamine is a key neuromodulator" in chunk.text


def test_chunking_splits_on_speaker_change():
    segments = [
        _make_seg("What is the effect of cold plunge?", 0.0, 5.0, speaker="Lex Fridman"),
        _make_seg("Cold exposure increases dopamine for hours.", 5.0, 12.0, speaker="Andrew Huberman"),
    ]
    chunks = chunk_segments(segments, target_words=100, overlap_words=10)

    assert len(chunks) == 2
    assert chunks[0].speaker == "Lex Fridman"
    assert chunks[1].speaker == "Andrew Huberman"
