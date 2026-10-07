"""Transcript domain models: Segment, Chunk, and Show."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Show = Literal["huberman_lab", "joe_rogan_experience", "lex_fridman_podcast"]


class Segment(BaseModel):
    show: Show
    episode_id: str = Field(min_length=1)
    episode_title: str
    speaker: str = Field(min_length=1)
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(ge=0)
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def _end_after_start(self) -> "Segment":
        if self.end_seconds < self.start_seconds:
            raise ValueError("end_seconds must be >= start_seconds")
        return self

    @property
    def timestamp(self) -> str:
        """Human-readable start time for citations, e.g. '01:12:04'."""
        s = int(self.start_seconds)
        return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


class Chunk(BaseModel):
    chunk_id: str = Field(min_length=1)
    show: Show
    episode_id: str = Field(min_length=1)
    episode_title: str
    speaker: str = Field(min_length=1)
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(ge=0)
    text: str = Field(min_length=1)

    @property
    def timestamp(self) -> str:
        s = int(self.start_seconds)
        return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"

    def to_metadata(self) -> dict:
        """Flatten fields for ChromaDB metadata (scalar values: str, int, float, bool)."""
        return {
            "chunk_id": self.chunk_id,
            "show": self.show,
            "episode_id": self.episode_id,
            "episode_title": self.episode_title,
            "speaker": self.speaker,
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "timestamp": self.timestamp,
        }
