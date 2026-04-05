# utils/gemini_handler.py — Gemini AI handler (updated to use ModelManager)
import logging

logger = logging.getLogger(__name__)


class GeminiAI:
    """Thin wrapper around a genai.GenerativeModel for summarization and Q&A."""

    def __init__(self, model):
        """Accept an already-initialised GenerativeModel instance."""
        self.model = model

    def generate_summary(self, text: str, domain: str) -> str:
        """Generate domain-specific summary for a single text block."""
        prompt = f"""Summarize this {domain} document:

{text}

Provide a comprehensive summary with:
1. Key points and main ideas
2. Important details specific to {domain}
3. Recommendations or insights
Use markdown formatting with headings and bullet points."""

        try:
            response = self.model.generate_content(prompt)
            return response.text if response and response.text else "Summary generation failed."
        except Exception as exc:
            logger.error("Summary generation failed: %s", exc)
            return f"**AI Error:** {exc}"

    def answer_question(self, context: str, question: str, domain: str) -> str:
        """Answer a question grounded in the provided context."""
        prompt = f"""Context ({domain} document):
{context}

Question: {question}

Answer based ONLY on the document above. If the answer isn't in the document, say so.
Provide quotes and references where possible. Format with clear sections."""

        try:
            response = self.model.generate_content(prompt)
            return response.text if response and response.text else "Could not generate an answer."
        except Exception as exc:
            logger.error("Q&A failed: %s", exc)
            return f"**AI Error:** {exc}"
