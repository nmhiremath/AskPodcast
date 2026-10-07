import pytest
from pydantic import ValidationError

from app.schemas import Segment


def make(**overrides) -> dict:
    base = dict(
        show="huberman_lab",
        episode_id="hl-039",
        episode_title="Controlling Your Dopamine",
        speaker="Andrew Huberman",
        start_seconds=4324,
        end_seconds=4351,
        text="Dopamine is less about pleasure and more about motivation.",
    )
    return base | overrides


def test_valid_segment_and_timestamp():
    seg = Segment(**make())
    assert seg.timestamp == "01:12:04"


def test_rejects_unknown_show():
    with pytest.raises(ValidationError):
        Segment(**make(show="some_other_podcast"))


def test_rejects_end_before_start():
    with pytest.raises(ValidationError):
        Segment(**make(start_seconds=100, end_seconds=50))
