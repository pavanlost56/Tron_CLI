"""Embedding manager for creating and handling embeddings."""

from sentence_transformers import SentenceTransformer
from ..core.config import settings

class EmbeddingManager:
    """Manage embeddings using a pre-trained language model."""

    def __init__(self, model_name: str = None):
        """Initialize with a chosen embedding model name."""
        model_name = model_name or settings.embedding_model
        self.model = SentenceTransformer(model_name)

    def create_embedding(self, text: str) -> list:
        """Create an embedding for the provided text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def batch_create_embeddings(self, texts: list) -> list:
        """Create embeddings for a batch of texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
