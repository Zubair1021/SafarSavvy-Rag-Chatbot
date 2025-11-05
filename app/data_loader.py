import os
import logging
from typing import List

from app.vector_store import VectorStore

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join("data", "transport")
SEED_DOC_ID = "transport_seed"


def _read_text_files(paths: List[str]) -> str:
    contents: List[str] = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    contents.append(f"[Source: {os.path.basename(path)}]\n\n{text}")
        except Exception as e:
            logger.warning(f"Failed to read {path}: {e}")
    return "\n\n---\n\n".join(contents)


def _chunk_plain_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def seed_transport_knowledge_if_needed(vector_store: VectorStore) -> None:
    try:
        if not os.path.isdir(DATA_DIR):
            logger.info(f"No data directory found at {DATA_DIR}; skipping seeding.")
            return

        # If already indexed, skip
        stats = vector_store.get_document_chunks(SEED_DOC_ID)
        if isinstance(stats, dict) and stats.get("chunk_count", 0) > 0:
            logger.info("Transport seed knowledge already indexed; skipping seeding.")
            return

        # Collect files
        files: List[str] = []
        for root, _, filenames in os.walk(DATA_DIR):
            for name in filenames:
                if name.lower().endswith((".md", ".txt")):
                    files.append(os.path.join(root, name))
        if not files:
            logger.info("No seed files found to index.")
            return

        # Read and chunk
        logger.info(f"Indexing transport seed knowledge from {len(files)} files...")
        merged_text = _read_text_files(files)
        chunks = _chunk_plain_text(merged_text, chunk_size=400, overlap=60)
        if not chunks:
            logger.info("No content found in seed files; skipping.")
            return

        # Add to vector store
        vector_store.add_document(SEED_DOC_ID, chunks)
        logger.info("Transport seed knowledge indexed successfully.")
    except Exception as e:
        logger.error(f"Failed to seed transport knowledge: {e}")

