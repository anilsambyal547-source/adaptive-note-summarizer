# utils/rag_engine.py — FAISS-based retrieval-augmented generation
import logging

logger = logging.getLogger(__name__)

# Guard heavy imports behind a flag so the app starts even if deps are missing.
_FAISS_AVAILABLE = False
_embedder = None

try:
    import faiss
    import numpy as np
    _FAISS_AVAILABLE = True
except ImportError:
    logger.info("faiss-cpu not installed — RAG will fall back to full-text context")


def _get_embedder():
    """Lazy-load the sentence-transformer model (heavy; load once)."""
    global _embedder
    if _embedder is not None:
        return _embedder
    try:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return _embedder
    except ImportError:
        logger.info("sentence-transformers not installed — RAG disabled")
        return None


class RAGEngine:
    """
    Per-document retrieval engine.

    Usage:
        engine = RAGEngine()
        engine.index(chunks)
        context = engine.query("What is X?", top_k=5)
    """

    def __init__(self):
        self.chunks: list[str] = []
        self.index_store = None  # FAISS index
        self._embeddings = None
        self.ready = False

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index(self, chunks: list[str]) -> bool:
        """Encode chunks and build a FAISS index. Returns True on success."""
        if not _FAISS_AVAILABLE:
            logger.info("FAISS not available — storing chunks for full-text fallback")
            self.chunks = chunks
            return False

        embedder = _get_embedder()
        if embedder is None:
            self.chunks = chunks
            return False

        self.chunks = chunks

        try:
            import numpy as np
            embeddings = embedder.encode(chunks, show_progress_bar=False)
            embeddings = np.array(embeddings, dtype="float32")

            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)

            dim = embeddings.shape[1]
            self.index_store = faiss.IndexFlatIP(dim)  # inner-product after normalization = cosine
            self.index_store.add(embeddings)
            self._embeddings = embeddings
            self.ready = True
            logger.info("FAISS index built: %d chunks, dim=%d", len(chunks), dim)
            return True
        except Exception as exc:
            logger.error("FAISS indexing failed: %s", exc)
            self.ready = False
            return False

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def query(self, question: str, top_k: int = 5) -> list[str]:
        """Return the *top_k* most relevant chunks for *question*."""
        if self.ready and self.index_store is not None:
            return self._faiss_query(question, top_k)
        # Fallback: return first top_k chunks (positional)
        return self.chunks[:top_k]

    def build_context(self, question: str, top_k: int = 5, max_chars: int = 6000) -> str:
        """Retrieve relevant chunks and concatenate into a context string."""
        relevant = self.query(question, top_k=top_k)
        context_parts: list[str] = []
        total = 0
        for chunk in relevant:
            if total + len(chunk) > max_chars:
                break
            context_parts.append(chunk)
            total += len(chunk)
        return "\n\n---\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _faiss_query(self, question: str, top_k: int) -> list[str]:
        embedder = _get_embedder()
        if embedder is None:
            return self.chunks[:top_k]

        try:
            import numpy as np
            q_emb = embedder.encode([question])
            q_emb = np.array(q_emb, dtype="float32")
            faiss.normalize_L2(q_emb)

            k = min(top_k, len(self.chunks))
            _, indices = self.index_store.search(q_emb, k)

            results = []
            for idx in indices[0]:
                if 0 <= idx < len(self.chunks):
                    results.append(self.chunks[idx])
            return results
        except Exception as exc:
            logger.error("FAISS query failed: %s", exc)
            return self.chunks[:top_k]
