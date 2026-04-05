# tests/test_ocr.py — Unit tests for the OCR processor
import pytest
from unittest.mock import patch, MagicMock
from utils.ocr_processor import (
    OCRResult,
    extract_text_from_image,
    extract_text_with_vision,
    extract_text_with_tesseract,
)


class TestOCRResult:
    def test_default_values(self):
        r = OCRResult()
        assert r.text == ""
        assert r.method == "none"
        assert r.warnings == []
        assert not r.success


class TestExtractTextWithVision:
    def test_success(self, sample_image_bytes):
        model = MagicMock()
        resp = MagicMock()
        resp.text = "Extracted text from image using vision model"
        model.generate_content.return_value = resp

        result = extract_text_with_vision(sample_image_bytes, model)
        assert result.success
        assert result.method == "gemini_vision"
        assert "Extracted text" in result.text

    def test_empty_response(self, sample_image_bytes):
        model = MagicMock()
        resp = MagicMock()
        resp.text = ""
        model.generate_content.return_value = resp

        result = extract_text_with_vision(sample_image_bytes, model)
        assert not result.success

    def test_exception(self, sample_image_bytes):
        model = MagicMock()
        model.generate_content.side_effect = Exception("API down")

        result = extract_text_with_vision(sample_image_bytes, model)
        assert not result.success
        assert any("failed" in w.lower() for w in result.warnings)


class TestExtractTextWithTesseract:
    def test_success(self, sample_image_bytes):
        mock_tess = MagicMock()
        mock_tess.image_to_string.return_value = "OCR extracted text content here"
        with patch.dict("sys.modules", {"pytesseract": mock_tess}):
            result = extract_text_with_tesseract(sample_image_bytes)
        assert result.success
        assert result.method == "tesseract_ocr"

    def test_empty_result(self, sample_image_bytes):
        mock_tess = MagicMock()
        mock_tess.image_to_string.return_value = ""
        with patch.dict("sys.modules", {"pytesseract": mock_tess}):
            result = extract_text_with_tesseract(sample_image_bytes)
        assert not result.success

    def test_import_error(self, sample_image_bytes):
        """If pytesseract is not installed, should return graceful error."""
        result = extract_text_with_tesseract(sample_image_bytes)
        # May or may not fail depending on environment, but shouldn't crash
        assert isinstance(result, OCRResult)


class TestExtractTextFromImage:
    def test_vision_first(self, sample_image_bytes):
        """Should try vision before Tesseract."""
        model = MagicMock()
        resp = MagicMock()
        resp.text = "Vision extracted this text successfully"
        model.generate_content.return_value = resp

        result = extract_text_from_image(sample_image_bytes, model=model)
        assert result.success
        assert result.method == "gemini_vision"

    @patch("utils.ocr_processor.extract_text_with_tesseract")
    def test_falls_back_to_tesseract(self, mock_tess, sample_image_bytes):
        """If vision fails, should fall back to Tesseract."""
        mock_tess.return_value = OCRResult(
            text="Tesseract got this", method="tesseract_ocr", success=True
        )

        # Model that fails
        model = MagicMock()
        model.generate_content.side_effect = Exception("Vision failed")

        result = extract_text_from_image(sample_image_bytes, model=model)
        assert result.success
        assert result.method == "tesseract_ocr"

    def test_no_model_provided(self, sample_image_bytes):
        """Without a model, should skip vision and try Tesseract only."""
        result = extract_text_from_image(sample_image_bytes, model=None)
        # Result depends on Tesseract availability; should not crash
        assert isinstance(result, OCRResult)
