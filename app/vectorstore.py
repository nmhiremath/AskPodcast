"""Vector store wrapper around ChromaDB and Gemini embeddings.

Persists collections locally to disk and supports filtered similarity search.
"""
import os
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.schemas import Chunk

load_dotenv()

DEFAULT_DB_DIR = "chroma_db"
DEFAULT_COLLECTION = "podcast_transcripts"


def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """Load embedding model configured in .env."""
    model_name = os.environ.get("EMBEDDING_MODEL", "models/gemini-embedding-2")
    return GoogleGenerativeAIEmbeddings(model=model_name)


def get_vectorstore(
    persist_directory: str = DEFAULT_DB_DIR,
    collection_name: str = DEFAULT_COLLECTION,
) -> Chroma:
    """Create or connect to a local persistent ChromaDB collection."""
    embeddings = get_embedding_model()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )


def index_chunks(chunks: list[Chunk], vectorstore: Chroma | None = None) -> int:
    """Convert Chunks into LangChain Documents and index them in ChromaDB.
    
    Returns the number of indexed chunks.
    """
    if not chunks:
        return 0

    if vectorstore is None:
        vectorstore = get_vectorstore()

    docs = [
        Document(
            page_content=chunk.text,
            metadata=chunk.to_metadata(),
            id=chunk.chunk_id,
        )
        for chunk in chunks
    ]

    vectorstore.add_documents(docs)
    return len(docs)


def similarity_search_with_scores(
    query: str,
    k: int = 4,
    where: dict[str, Any] | None = None,
    vectorstore: Chroma | None = None,
) -> list[tuple[Document, float]]:
    """Retrieve top-k documents along with cosine relevance scores."""
    if vectorstore is None:
        vectorstore = get_vectorstore()

    return vectorstore.similarity_search_with_score(
        query=query,
        k=k,
        filter=where,
    )
