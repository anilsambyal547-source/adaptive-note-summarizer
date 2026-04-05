# utils/chunker.py — Semantic chunking and map-reduce summarization
import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def semantic_chunk(
    text: str,
    max_chunk_size: int = 2000,
    overlap: int = 200,
) -> list[str]:
    """
    Split text into semantically coherent chunks.

    Strategy:
    1. Split on double-newlines (paragraphs / sections).
    2. Merge small paragraphs into chunks up to *max_chunk_size*.
    3. Maintain *overlap* characters between consecutive chunks.
    """
    if not text or not text.strip():
        return []

    # Split on section/paragraph boundaries
    paragraphs = re.split(r"\n{2,}", text.strip())
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return [text.strip()] if text.strip() else []

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for para in paragraphs:
        para_len = len(para)

        # If a single paragraph exceeds max_chunk_size, split it further
        if para_len > max_chunk_size:
            # Flush current buffer first
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_length = 0

            # Hard-split the large paragraph by sentences
            sentences = re.split(r"(?<=[.!?])\s+", para)
            sub_chunk: list[str] = []
            sub_length = 0
            for sent in sentences:
                if sub_length + len(sent) > max_chunk_size and sub_chunk:
                    chunks.append(" ".join(sub_chunk))
                    # Overlap: keep last part
                    overlap_text = " ".join(sub_chunk)[-overlap:] if overlap else ""
                    sub_chunk = [overlap_text] if overlap_text else []
                    sub_length = len(overlap_text)
                sub_chunk.append(sent)
                sub_length += len(sent)
            if sub_chunk:
                chunks.append(" ".join(sub_chunk))
            continue

        # Try to merge into current chunk
        if current_length + para_len + 2 > max_chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            # Overlap: carry tail of previous chunk
            if overlap > 0:
                tail = "\n\n".join(current_chunk)
                overlap_text = tail[-overlap:]
                current_chunk = [overlap_text]
                current_length = len(overlap_text)
            else:
                current_chunk = []
                current_length = 0

        current_chunk.append(para)
        current_length += para_len + 2  # account for \n\n

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


# ---------------------------------------------------------------------------
# Map-Reduce Summarization
# ---------------------------------------------------------------------------

def map_reduce_summarize(
    chunks: list[str],
    model,
    doc_type: str = "General",
    progress_callback=None,
) -> str:
    """
    Summarize a document via map-reduce.

    Map:   summarize each chunk independently.
    Reduce: merge chunk summaries into a single final summary.
    """
    if not chunks:
        return "No content to summarize."

    # If the text fits in one chunk, just summarize directly
    if len(chunks) == 1:
        return _summarize_single(chunks[0], model, doc_type)

    # --- Map phase ---
    chunk_summaries: list[str] = []
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_callback(i, total, "map")

        summary = _summarize_single(chunk, model, doc_type, is_chunk=True, chunk_num=i + 1)
        chunk_summaries.append(summary)

    if progress_callback:
        progress_callback(total, total, "map")

    # --- Reduce phase ---
    if progress_callback:
        progress_callback(0, 1, "reduce")

    combined = "\n\n---\n\n".join(
        f"**Chunk {i + 1}:**\n{s}" for i, s in enumerate(chunk_summaries)
    )

    reduce_prompt = f"""You are given summaries of different sections of a {doc_type} document.
Combine them into ONE coherent, comprehensive summary. Remove redundancy, preserve all
key information, and maintain logical flow.

SECTION SUMMARIES:
{combined}

FINAL COMBINED SUMMARY:"""

    try:
        response = model.generate_content(reduce_prompt)
        result = response.text if response and response.text else "Summary generation failed."
    except Exception as exc:
        logger.error("Reduce step failed: %s", exc)
        # Gracefully return the concatenated chunk summaries
        result = "## Section Summaries\n\n" + "\n\n".join(
            f"### Section {i + 1}\n{s}" for i, s in enumerate(chunk_summaries)
        )

    if progress_callback:
        progress_callback(1, 1, "reduce")

    return result


def _summarize_single(
    text: str,
    model,
    doc_type: str,
    is_chunk: bool = False,
    chunk_num: int = 0,
) -> str:
    """Summarize a single chunk or full text."""
    chunk_note = f" (section {chunk_num})" if is_chunk else ""
    prompt = f"""Summarize this {doc_type} document{chunk_note}:

{text}

Provide a comprehensive summary with key points. Use markdown formatting."""

    try:
        response = model.generate_content(prompt)
        return response.text if response and response.text else ""
    except Exception as exc:
        logger.error("Summarization failed for chunk %d: %s", chunk_num, exc)
        return f"*[Summary failed for section {chunk_num}: {exc}]*"
