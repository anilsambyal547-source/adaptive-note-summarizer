# tests/test_model_manager.py — Unit tests for dynamic model discovery
import pytest
from unittest.mock import patch, MagicMock


class TestModelManager:
    """Test ModelManager without actually calling the Gemini API."""

    @patch("utils.model_manager.genai")
    @patch("utils.model_manager.st")
    def test_dynamic_discovery_success(self, mock_st, mock_genai):
        """Should discover a working model via list_models."""
        from utils.model_manager import ModelManager

        mock_st.session_state = {}

        # Mock list_models to return one model
        mock_model_info = MagicMock()
        mock_model_info.name = "models/gemini-2.0-flash"
        mock_model_info.supported_generation_methods = ["generateContent"]
        mock_genai.list_models.return_value = [mock_model_info]

        # Mock GenerativeModel
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "OK"
        mock_instance.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_instance

        mgr = ModelManager(api_key="test-key")
        result = mgr.discover_and_init()

        assert result is not None
        assert mgr.is_active

    @patch("utils.model_manager.genai")
    @patch("utils.model_manager.st")
    def test_fallback_to_static_list(self, mock_st, mock_genai):
        """When dynamic listing fails, should try static models."""
        from utils.model_manager import ModelManager

        mock_st.session_state = {}

        # list_models fails
        mock_genai.list_models.side_effect = Exception("Network error")

        # But static model works
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "OK"
        mock_instance.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_instance

        mgr = ModelManager(api_key="test-key")
        result = mgr.discover_and_init()

        assert result is not None

    @patch("utils.model_manager.genai")
    @patch("utils.model_manager.st")
    def test_all_models_fail(self, mock_st, mock_genai):
        """When all models fail, should return None and set error."""
        from utils.model_manager import ModelManager

        mock_st.session_state = {}
        mock_genai.list_models.return_value = []
        mock_genai.GenerativeModel.side_effect = Exception("Model unavailable")

        mgr = ModelManager(api_key="test-key")
        result = mgr.discover_and_init()

        assert result is None
        assert not mgr.is_active
        assert mgr.error

    @patch("utils.model_manager.genai")
    @patch("utils.model_manager.st")
    def test_vision_detection(self, mock_st, mock_genai):
        """Should detect vision capability from model name."""
        from utils.model_manager import ModelManager

        mock_st.session_state = {}

        mock_model_info = MagicMock()
        mock_model_info.name = "models/gemini-2.0-flash"
        mock_model_info.supported_generation_methods = ["generateContent"]
        mock_genai.list_models.return_value = [mock_model_info]

        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "OK"
        mock_instance.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_instance

        mgr = ModelManager(api_key="test-key")
        mgr.discover_and_init()

        assert mgr.is_vision_capable
