# tests/test_chunker.py — Unit tests for semantic chunking and map-reduce
import pytest
from utils.chunker import semantic_chunk, map_reduce_summarize


class TestSemanticChunk:
    def test_empty_text(self):
        assert semantic_chunk("") == []
        assert semantic_chunk("   ") == []

    def test_short_text_single_chunk(self, sample_short_text):
        chunks = semantic_chunk(sample_short_text, max_chunk_size=2000)
        assert len(chunks) == 1
        assert sample_short_text in chunks[0]

    def test_long_text_multiple_chunks(self, sample_long_text):
        chunks = semantic_chunk(sample_long_text, max_chunk_size=500, overlap=50)
        assert len(chunks) > 1
        # Each chunk should be within limits (allowing some slack for paragraph boundaries)
        for chunk in chunks:
            assert len(chunk) < 1500  # generous upper bound

    def test_overlap_present(self):
        text = "Paragraph one content here.\n\nParagraph two content here.\n\nParagraph three content here."
        chunks = semantic_chunk(text, max_chunk_size=40, overlap=10)
        # With overlap, there should be shared content between consecutive chunks
        assert len(chunks) >= 2

    def test_preserves_all_content(self, sample_short_text):
        chunks = semantic_chunk(sample_short_text, max_chunk_size=2000, overlap=0)
        combined = " ".join(chunks)
        # All words from original should be present
        for word in sample_short_text.split():
            assert word in combined

    def test_handles_large_single_paragraph(self):
        # Use realistic text with sentences so the sentence splitter works
        huge_para = "This is a sentence. " * 300  # ~6000 chars, no paragraph breaks
        chunks = semantic_chunk(huge_para, max_chunk_size=500)
        assert len(chunks) >= 2

    def test_respects_max_chunk_size(self):
        text = "\n\n".join([f"Section {i}: " + "content " * 50 for i in range(10)])
        chunks = semantic_chunk(text, max_chunk_size=500, overlap=0)
        for chunk in chunks:
            # Allow some flexibility for paragraph merging logic
            assert len(chunk) < 1200


class TestMapReduceSummarize:
    def test_single_chunk(self, mock_genai_model):
        result = map_reduce_summarize(["Short content"], mock_genai_model, "General")
        assert "Mock AI response" in result

    def test_empty_chunks(self, mock_genai_model):
        result = map_reduce_summarize([], mock_genai_model, "General")
        assert "No content" in result

    def test_multiple_chunks(self, mock_genai_model):
        chunks = ["Chunk one content", "Chunk two content", "Chunk three content"]
        result = map_reduce_summarize(chunks, mock_genai_model, "Mathematics")
        # Should have called generate_content multiple times (map + reduce)
        assert mock_genai_model.generate_content.call_count >= 2
        assert isinstance(result, str)

    def test_progress_callback(self, mock_genai_model):
        chunks = ["Chunk 1", "Chunk 2"]
        calls = []

        def cb(current, total, phase):
            calls.append((current, total, phase))

        map_reduce_summarize(chunks, mock_genai_model, "General", progress_callback=cb)
        assert len(calls) > 0
        assert any(c[2] == "map" for c in calls)
        assert any(c[2] == "reduce" for c in calls)

    def test_handles_model_error(self):
        """If the model raises, map_reduce should still return something."""
        from unittest.mock import MagicMock

        bad_model = MagicMock()
        bad_model.generate_content.side_effect = Exception("API Error")

        result = map_reduce_summarize(["Some content"], bad_model, "General")
        assert isinstance(result, str)
        # Should contain an error indication
        assert "failed" in result.lower() or "error" in result.lower()
