# utils/classifier.py — Domain classifier for document type detection
import re


class DomainClassifier:
    """Detects if document is Mathematics, Literature, or General."""

    @staticmethod
    def classify(text: str) -> str:
        """Classify text into a domain."""
        text_lower = text.lower()

        math_terms = [
            "equation", "formula", "theorem", "proof", "derivative",
            "integral", "calculate", "solve for", "matrix", "algebra",
            "polynomial", "logarithm", "trigonometry", "calculus",
        ]
        lit_terms = [
            "chapter", "character", "plot", "theme", "symbolism",
            "metaphor", "novel", "story", "author", "literary",
            "narrator", "protagonist", "antagonist", "allegory",
        ]

        math_score = sum(1 for term in math_terms if term in text_lower)
        lit_score = sum(1 for term in lit_terms if term in text_lower)

        if math_score > lit_score and math_score > 2:
            return "Mathematics"
        if lit_score > math_score and lit_score > 2:
            return "Literature"
        return "General"

    @staticmethod
    def get_domain_info(domain: str) -> dict:
        """Get display metadata for a domain."""
        info = {
            "Mathematics": {
                "icon": "🔢",
                "color": "#FF6B6B",
                "description": "Mathematical documents with equations, proofs, and formulas",
            },
            "Literature": {
                "icon": "📖",
                "color": "#4ECDC4",
                "description": "Literary works, novels, poems, and analysis",
            },
            "General": {
                "icon": "📄",
                "color": "#45B7D1",
                "description": "General documents, reports, articles, and notes",
            },
        }
        return info.get(domain, info["General"])
