"""API request and response schemas."""
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Structured citation metadata for clickable UI elements."""
    episode_title: str
    episode_id: str
    speaker: str
    timestamp: str
    start_seconds: float
    url: str


class AskRequest(BaseModel):
    """Incoming user query payload."""
    question: str = Field(min_length=3, max_length=500, description="Question to ask the podcast archive.")


class AskResponse(BaseModel):
    """Structured answer response with citations and execution metadata."""
    question: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    rewrites_attempted: int = 0
    relevant_chunks_used: int = 0
