# utils/api_key_manager.py — Multi-key management with rotation and usage tracking
import streamlit as st
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages one or more Gemini API keys with rotation and usage tracking."""

    SESSION_KEY = "_api_key_mgr"

    def __init__(self):
        state = self._state()
        if "keys" not in state:
            state["keys"] = self._load_keys()
            state["current_index"] = 0
            state["usage"] = {i: 0 for i in range(len(state["keys"]))}
            state["quota_limit"] = 1500  # requests per key before warning

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def current_key(self) -> str | None:
        state = self._state()
        keys = state.get("keys", [])
        if not keys:
            return None
        idx = state.get("current_index", 0)
        return keys[idx]

    def record_usage(self):
        """Increment usage counter for the current key."""
        state = self._state()
        idx = state.get("current_index", 0)
        state["usage"][idx] = state["usage"].get(idx, 0) + 1

    def rotate_key(self) -> str | None:
        """Switch to the next available key. Returns the new key or None."""
        state = self._state()
        keys = state.get("keys", [])
        if len(keys) <= 1:
            return self.current_key
        idx = (state.get("current_index", 0) + 1) % len(keys)
        state["current_index"] = idx
        logger.info("Rotated to API key index %d", idx)
        return keys[idx]

    def get_usage_info(self) -> dict:
        """Return usage stats for the current key."""
        state = self._state()
        idx = state.get("current_index", 0)
        used = state["usage"].get(idx, 0)
        limit = state.get("quota_limit", 1500)
        return {
            "key_index": idx,
            "total_keys": len(state.get("keys", [])),
            "requests_used": used,
            "quota_limit": limit,
            "near_quota": used >= limit * 0.8,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _state() -> dict:
        if APIKeyManager.SESSION_KEY not in st.session_state:
            st.session_state[APIKeyManager.SESSION_KEY] = {}
        return st.session_state[APIKeyManager.SESSION_KEY]

    @staticmethod
    def _load_keys() -> list[str]:
        """Load keys from st.secrets or environment."""
        keys: list[str] = []

        # Try comma-separated list first
        try:
            raw = st.secrets.get("GEMINI_API_KEYS", "")
            if raw:
                keys = [k.strip() for k in raw.split(",") if k.strip()]
        except Exception:
            pass

        # Fall back to single key
        if not keys:
            try:
                single = st.secrets.get("GEMINI_API_KEY", "")
                if single:
                    keys = [single.strip()]
            except Exception:
                pass

        # Last resort: environment variable
        if not keys:
            import os

            env_key = os.getenv("GEMINI_API_KEY", "")
            if env_key:
                keys = [env_key.strip()]

        if not keys:
            logger.warning("No Gemini API keys found in secrets or environment")

        return keys
