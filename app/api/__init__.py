"""FastAPI application initialization for AskPodcast."""
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AskPodcast API",
    description="Corrective RAG Chatbot indexing podcast transcripts with clickable timestamp citations.",
    version="0.1.0",
)

app.include_router(router)

__all__ = ["app"]
