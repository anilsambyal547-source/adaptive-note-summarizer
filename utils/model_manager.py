# utils/model_manager.py — Dynamic model discovery with fallback
import google.generativeai as genai
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Static fallback list — used only when dynamic discovery fails.
STATIC_MODELS = [
    "models/gemini-2.0-flash",
    "models/gemini-2.0-flash-001",
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemini-1.0-pro",
]


class ModelManager:
    """Discover, initialise, and manage Gemini generative models."""

    SESSION_KEY = "_model_mgr"

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def discover_and_init(self) -> str | None:
        """Find a working model. Returns model name on success, None on failure."""
        state = self._state()

        # 1. Try dynamic discovery
        candidates = self._dynamic_candidates()

        # 2. Merge with static fallback (deduplicate, keep order)
        seen = set()
        ordered: list[str] = []
        for name in candidates + STATIC_MODELS:
            if name not in seen:
                seen.add(name)
                ordered.append(name)

        # 3. Try each candidate
        for name in ordered:
            model = self._try_model(name)
            if model is not None:
                state["model"] = model
                state["model_name"] = name
                state["active"] = True
                state["error"] = ""
                logger.info("Model ready: %s", name)
                return name

        state["active"] = False
        state["error"] = "No working model found after trying all candidates."
        return None

    @property
    def model(self):
        return self._state().get("model")

    @property
    def model_name(self) -> str:
        return self._state().get("model_name", "unknown")

    @property
    def is_active(self) -> bool:
        return self._state().get("active", False)

    @property
    def error(self) -> str:
        return self._state().get("error", "")

    @property
    def is_vision_capable(self) -> bool:
        """Check if current model supports image input."""
        name = self.model_name.lower()
        # Gemini 1.5+ and 2.x models support vision
        return any(v in name for v in ("1.5", "2.0", "2.5", "flash", "pro-vision"))

    def reset(self):
        """Clear cached model state so next call re-discovers."""
        st.session_state.pop(self.SESSION_KEY, None)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _state() -> dict:
        if ModelManager.SESSION_KEY not in st.session_state:
            st.session_state[ModelManager.SESSION_KEY] = {}
        return st.session_state[ModelManager.SESSION_KEY]

    @staticmethod
    def _dynamic_candidates() -> list[str]:
        """Query the API for models that support generateContent."""
        try:
            models = genai.list_models()
            return [
                m.name
                for m in models
                if "generateContent" in (m.supported_generation_methods or [])
            ]
        except Exception as exc:
            logger.warning("Dynamic model listing failed: %s", exc)
            return []

    @staticmethod
    def _try_model(name: str):
        """Attempt to create a model and run a minimal health-check."""
        try:
            model = genai.GenerativeModel(name)
            resp = model.generate_content("Respond with OK")
            if resp and resp.text:
                return model
        except Exception as exc:
            logger.debug("Model %s failed: %s", name, exc)
        return None
