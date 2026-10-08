"""State definition for the Corrective RAG LangGraph agent."""

from langchain_core.documents import Document
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """The central state of our podcast RAG agent.

    Each node in LangGraph receives this state dictionary and
    returns a dictionary updating one or more of these keys.
    """

    # The active question (original or rewritten)
    question: str

    # Raw chunks retrieved from ChromaDB
    documents: list[Document]

    # Filtered chunks that passed the relevance grader
    relevant_documents: list[Document]

    # Loop circuit-breaker: incremented each time query is rewritten
    rewrite_count: int

    # Final answer generated with timestamp citations
    generation: str
