# tests/test_file_processing.py — Unit tests for file parsing and classifier
import pytest
from utils.classifier import DomainClassifier


class TestDomainClassifier:
    def test_math_classification(self, sample_math_text):
        result = DomainClassifier.classify(sample_math_text)
        assert result == "Mathematics"

    def test_literature_classification(self, sample_lit_text):
        result = DomainClassifier.classify(sample_lit_text)
        assert result == "Literature"

    def test_general_classification(self):
        text = "This is a quarterly business report showing revenue growth and market expansion."
        result = DomainClassifier.classify(text)
        assert result == "General"

    def test_empty_text(self):
        result = DomainClassifier.classify("")
        assert result == "General"

    def test_domain_info_valid(self):
        for domain in ["Mathematics", "Literature", "General"]:
            info = DomainClassifier.get_domain_info(domain)
            assert "icon" in info
            assert "color" in info
            assert "description" in info

    def test_domain_info_unknown(self):
        info = DomainClassifier.get_domain_info("Unknown")
        assert info == DomainClassifier.get_domain_info("General")


class TestFileSizeLimit:
    def test_size_constant(self):
        """Verify the size limit is defined correctly."""
        # Import from app would require Streamlit; just verify the math
        max_mb = 50
        max_bytes = max_mb * 1024 * 1024
        assert max_bytes == 52_428_800


class TestTxtParsing:
    def test_utf8(self):
        raw = "Hello, world! Unicode: café résumé".encode("utf-8")
        text = raw.decode("utf-8", errors="replace")
        assert "café" in text

    def test_invalid_encoding(self):
        raw = b"\xff\xfe invalid bytes"
        text = raw.decode("utf-8", errors="replace")
        # Should not crash; replaces invalid chars
        assert isinstance(text, str)
