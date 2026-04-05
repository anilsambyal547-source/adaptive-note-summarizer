# tests/conftest.py — Shared fixtures for the test suite
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_genai_model():
    """A mock genai.GenerativeModel that returns predictable text."""
    model = MagicMock()
    response = MagicMock()
    response.text = "Mock AI response"
    model.generate_content.return_value = response
    return model


@pytest.fixture
def sample_short_text():
    return "This is a short test document with minimal content."


@pytest.fixture
def sample_long_text():
    """A long document that exceeds the 2000-char chunk size."""
    paragraph = (
        "This is a detailed paragraph about machine learning algorithms. "
        "Neural networks have revolutionized the field of artificial intelligence "
        "by enabling computers to learn from data. Deep learning, a subset of "
        "machine learning, uses multi-layered neural networks to extract "
        "higher-level features from raw input. Convolutional neural networks "
        "are particularly effective for image recognition tasks.\n\n"
    )
    return paragraph * 20  # ~3000+ characters


@pytest.fixture
def sample_math_text():
    return (
        "CALCULUS NOTES\n\n"
        "The derivative of a function measures the rate of change. "
        "The fundamental theorem of calculus links differentiation and integration.\n\n"
        "Key formulas:\n"
        "- Derivative: f'(x) = lim(h→0) [f(x+h) - f(x)]/h\n"
        "- Integral: ∫ x² dx = (x³/3) + C\n"
        "- Chain Rule: d/dx[f(g(x))] = f'(g(x)) · g'(x)\n\n"
        "Theorem: Every continuous function on a closed interval is integrable.\n"
        "Proof involves constructing Riemann sums and showing convergence.\n"
        "The equation for a parabola is y = ax² + bx + c.\n"
        "Solve for x using the quadratic formula.\n"
        "Matrix multiplication is not commutative in general.\n"
        "Algebra provides the foundation for higher mathematics."
    )


@pytest.fixture
def sample_lit_text():
    return (
        "PRIDE AND PREJUDICE\n\n"
        "Chapter 1: It is a truth universally acknowledged.\n"
        "The main character Elizabeth Bennet navigates themes of love and pride.\n"
        "The plot revolves around the Bennet family's quest for suitable marriages.\n"
        "Symbolism abounds in the novel's depiction of estates.\n"
        "The author Jane Austen uses metaphor and irony throughout.\n"
        "Literary analysis reveals deep social commentary.\n"
        "The story explores class and prejudice in Regency England.\n"
        "The protagonist shows growth through the narrative."
    )


@pytest.fixture
def sample_pdf_bytes():
    """Minimal valid PDF bytes for testing."""
    import io
    from unittest.mock import patch

    # Create a simple in-memory PDF-like structure
    # For unit tests we mock PyPDF2 rather than creating a real PDF
    return b"%PDF-1.4 fake pdf content for testing"


@pytest.fixture
def sample_image_bytes():
    """Create a small test PNG image."""
    try:
        from PIL import Image
        img = Image.new("RGB", (100, 50), color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # Minimal 1x1 PNG
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
            b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
            b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )


import io
