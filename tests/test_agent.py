"""Tests for LangGraph agent structure and routing logic."""
from langchain_core.documents import Document

from app.agent.graph import MAX_REWRITES, build_graph, decide_to_generate


def test_graph_structure():
    """Verify LangGraph compiles and contains all 4 expected nodes."""
    graph = build_graph()
    node_names = set(graph.nodes.keys())
    expected = {"retrieve", "grade_documents", "rewrite_query", "generate"}
    assert expected.issubset(node_names)


def test_router_routes_to_generate_when_docs_present():
    state = {
        "question": "test",
        "documents": [],
        "relevant_documents": [Document(page_content="relevant text")],
        "rewrite_count": 0,
        "generation": "",
    }
    decision = decide_to_generate(state)
    assert decision == "generate"


def test_router_routes_to_rewrite_when_no_relevant_docs():
    state = {
        "question": "test",
        "documents": [],
        "relevant_documents": [],
        "rewrite_count": 0,
        "generation": "",
    }
    decision = decide_to_generate(state)
    assert decision == "rewrite_query"


def test_router_hits_circuit_breaker_after_max_rewrites():
    state = {
        "question": "test",
        "documents": [],
        "relevant_documents": [],
        "rewrite_count": MAX_REWRITES,
        "generation": "",
    }
    decision = decide_to_generate(state)
    assert decision == "generate"
