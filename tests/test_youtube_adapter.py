from app.ingestion.youtube import captions_to_segments

META = dict(
    show="huberman_lab",
    episode_id="yt-test",
    episode_title="Test Episode",
    speaker="Andrew Huberman",
)


def test_converts_and_cleans_captions():
    raw = [
        {"text": "[Music]", "start": 0.0, "duration": 2.0},
        {"text": "Welcome to the\nHuberman Lab podcast", "start": 2.0, "duration": 3.5},
    ]
    segs = captions_to_segments(raw, **META)

    assert len(segs) == 1                       # "[Music]" dropped
    assert segs[0].text == "Welcome to the Huberman Lab podcast"  # newline flattened
    assert segs[0].start_seconds == 2.0
    assert segs[0].end_seconds == 5.5           # start + duration
    assert segs[0].speaker == "Andrew Huberman"
