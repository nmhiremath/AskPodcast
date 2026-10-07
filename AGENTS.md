# AskPodcast — Agent & Developer Context

This document is the single source of truth for AI assistants and engineers working on this repository.

---

## 0. Strict 1-on-1 Tutoring & Pair Programming Protocol (MANDATORY)
1. **One File at a Time:** Never create or edit more than ONE file in a single turn.
2. **Concept & Plan First:** Never write or modify code before explaining the concept ("the why") and getting explicit approval from the user.
3. **Question Isolation:** If the user asks a question, answer the question ONLY. Do NOT write, modify, or run code in the same turn.
4. **Pacing & Checkpoints:** Stop after each step. Have the user inspect the file, run tests in their terminal, and answer a check-for-understanding question before proceeding.
5. **No Speculative Tool Execution:** Do not run test runners, build tools, or terminal commands unless the user explicitly requested them in their prompt.

---

## 1. Project Overview & Resume Item
- **Title:** Podcast Transcript Chatbot & Corrective RAG Agent
- **Target Shows:** Andrew Huberman (Huberman Lab), Joe Rogan, Lex Fridman. (Phase 1 focus: Huberman solo episodes).
- **Core Architecture:**
  - Ingestion: YouTube captions -> cleaned speaker `Segment`s -> sliding-window `Chunk`s (preserving start/end timestamp bounds).
  - Vector DB: ChromaDB collection storing chunks + scalar metadata for citation and filtering.
  - Orchestration: Stateful LangGraph implementing Self-RAG / Corrective RAG (Retrieve -> Grade relevance -> Fallback query rewrite -> Generate answer with timestamp citations).
  - API: FastAPI endpoint serving streaming/JSON answers.
  - Deployment: Docker container, pinned reproducible environment.

---

## 2. Tech Stack & Environment
- **Python:** 3.13 (`.venv` in project root)
- **Chat Model:** `gemini-3.8-flash` (configured in `.env`)
- **Embedding Model:** `models/gemini-embedding-2` (dim=3072, configured in `.env`)
- **Vector DB:** `chromadb>=1.5`
- **Orchestration:** `langchain>=1.4`, `langgraph>=1.2`, `langchain-google-genai>=4.4`
- **Validation:** Pydantic v2
- **Testing:** pytest

---

## 3. Directory Layout
```
AskPodcast/
├── AGENTS.md                  # LLM developer guide & invariants (this file)
├── requirements.txt           # Major-version bounded dependencies
├── pyproject.toml             # Pytest configuration
├── .env.example               # Secrets & model ID configuration template
├── data/
│   └── raw/                   # Git-ignored raw JSON transcripts by show
│       └── huberman_lab/
├── app/
│   ├── __init__.py
│   ├── schemas/               # Pydantic models (data & API)
│   │   ├── __init__.py
│   │   ├── transcripts.py     # Segment, Chunk, Show
│   │   └── api.py             # AskRequest, AskResponse, Citation
│   ├── ingestion/             # Transcript pipelines
│   │   ├── __init__.py
│   │   ├── chunking.py        # Pure sliding-window chunking
│   │   └── youtube.py         # YouTube adapter (oEmbed title, caption cleaning)
│   ├── vectorstore.py         # ChromaDB wrapper & embeddings
│   ├── agent/                 # LangGraph Self-RAG / CRAG workflow
│   │   ├── __init__.py
│   │   ├── state.py           # AgentState TypedDict
│   │   ├── nodes.py           # retrieve, grade, rewrite, generate
│   │   └── graph.py           # StateGraph & circuit-breaker
│   └── api/                   # FastAPI endpoints
│       ├── __init__.py        # FastAPI app mounting router
│       └── routes.py          # /health, /ask, /ask/stream
├── scripts/
│   ├── smoke_test_gemini.py   # Connectivity verification script
│   ├── list_models.py         # Inspect supported models for active API key
│   ├── fetch_episode.py       # CLI tool to download and cache episode transcript
│   ├── index_and_search.py    # Ingests cached episode into ChromaDB & searches
│   └── ask_agent.py           # Interactive CLI runner for Corrective RAG agent
└── tests/
    ├── test_schemas.py        # Contract validation tests
    ├── test_youtube_adapter.py# Offline adapter tests
    ├── test_chunking.py       # Boundary & speaker chunk tests
    ├── test_agent.py          # Graph routing & circuit-breaker tests
    └── test_api.py            # API health & validation tests
```

---

## 4. Key Engineering Invariants
1. **Isolated I/O:** Network operations (e.g., `fetch_raw_captions`) must stay strictly isolated from pure business transformations (`captions_to_segments`, `chunk_segments`). All unit tests run offline.
2. **Scalar Metadata Only:** ChromaDB metadata accepts only `str`, `int`, `float`, and `bool`. Always use `chunk.to_metadata()`.
3. **No Hardcoded Models:** Models are loaded from environment variables (`CHAT_MODEL`, `EMBEDDING_MODEL`), never hardcoded in logic.
4. **Timestamps as Floats:** Store timestamps as numerical seconds (`start_seconds: float`) for filtering and YouTube deep links (`&t=X`), and format to `"HH:MM:SS"` strings only for human display.

---

## 5. Developer Quick Commands
```bash
# Activate environment
source .venv/bin/activate

# Run test suite
python -m pytest -v

# Fetch & cache a test episode
python -m scripts.fetch_episode QmOF0crdyRU

# Test Gemini API connectivity
python scripts/smoke_test_gemini.py
```
