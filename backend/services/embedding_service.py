"""
backend/services/embedding_service.py
---------------------------------------
Local embedding generation using sentence-transformers. Runs entirely
on-device (CPU is fine) -- no API key, no rate limits, no network calls.

Model: sentence-transformers/all-mpnet-base-v2 (768-dim, matches existing
Qdrant collection vector size).
"""

from typing import List
from backend.core.logging import get_logger

logger = get_logger(__name__)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIM = 768


class EmbeddingService:
    """
    Lazy-loads the sentence-transformers model on first use (model loading
    takes a few seconds, so we don't want to pay that cost at import time
    or for requests that never need embeddings).
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading local embedding model (first call only)", model=self.model_name)
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of chunks for ingestion."""
        model = self._load()
        return model.encode(texts, convert_to_numpy=True, show_progress_bar=False).tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string for retrieval."""
        model = self._load()
        return model.encode(text, convert_to_numpy=True, show_progress_bar=False).tolist()


# Module-level singleton -- both ingestion_service and knowledge agent import this
embedding_service = EmbeddingService()
