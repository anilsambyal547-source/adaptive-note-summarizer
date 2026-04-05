# tests/test_rag.py — Unit tests for the RAG engine
import pytest
from unittest.mock import patch, MagicMock
from utils.rag_engine import RAGEngine


def _faiss_available() -> bool:
    try:
        import faiss
        return True
    except ImportError:
        return False


class TestRAGEngine:
    def test_init(self):
        engine = RAGEngine()
        assert engine.chunks == []
        assert not engine.ready

    def test_index_stores_chunks(self):
        engine = RAGEngine()
        chunks = ["First chunk", "Second chunk", "Third chunk"]
        engine.index(chunks)
        assert engine.chunks == chunks

    def test_query_fallback_without_faiss(self):
        """Without FAISS, query should return first N chunks."""
        engine = RAGEngine()
        engine.chunks = ["Alpha", "Beta", "Gamma", "Delta"]
        engine.ready = False

        results = engine.query("test question", top_k=2)
        assert len(results) == 2
        assert results[0] == "Alpha"
        assert results[1] == "Beta"

    def test_build_context_respects_max_chars(self):
        engine = RAGEngine()
        engine.chunks = ["A" * 3000, "B" * 3000, "C" * 3000]
        engine.ready = False

        context = engine.build_context("question", top_k=3, max_chars=5000)
        assert len(context) <= 6000  # max_chars + separator overhead

    def test_build_context_returns_string(self):
        engine = RAGEngine()
        engine.chunks = ["Hello world", "Foo bar"]
        engine.ready = False

        ctx = engine.build_context("question", top_k=5)
        assert isinstance(ctx, str)
        assert "Hello world" in ctx

    def test_query_empty_engine(self):
        engine = RAGEngine()
        results = engine.query("test", top_k=3)
        assert results == []

    @pytest.mark.skipif(
        not _faiss_available(),
        reason="faiss-cpu not installed"
    )
    def test_faiss_index_and_query(self):
        """Integration test — only runs if faiss + sentence-transformers available."""
        engine = RAGEngine()
        chunks = [
            "The Eiffel Tower is located in Paris, France.",
            "Machine learning uses algorithms to learn from data.",
            "Python is a popular programming language.",
            "The Great Wall of China is visible from space.",
            "Neural networks are inspired by the human brain.",
        ]
        success = engine.index(chunks)
        if not success:
            pytest.skip("Embedding model unavailable")

        results = engine.query("What is machine learning?", top_k=2)
        assert len(results) == 2
        # The most relevant chunk should be about ML
        assert any("machine learning" in r.lower() or "algorithm" in r.lower() for r in results)

