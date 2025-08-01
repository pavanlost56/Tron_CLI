"""Mistral AI client for CodeInsight."""
import logging
import os
from typing import List, Dict, Optional, Any, Union
import requests
from pydantic import BaseModel, Field
import numpy as np
from ..core.config import settings

logger = logging.getLogger(__name__)


class MistralConfig(BaseModel):
    """Configuration for Mistral AI client."""
    api_key: str = Field(default_factory=lambda: os.getenv("MISTRAL_API_KEY", ""))
    base_url: str = Field(default="https://api.mistral.ai")
    embedding_model: str = Field(default="mistral-embed")
    chat_model: str = Field(default="mistral-small")
    max_retries: int = Field(default=3)
    timeout: int = Field(default=30)


class MistralClient:
    """Client for interacting with Mistral AI API."""
    
    def __init__(self, config: Optional[MistralConfig] = None):
        self.config = config or MistralConfig()
        if not self.config.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """Make a request to the Mistral API."""
        url = f"{self.config.base_url}{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise
    
    def create_embeddings(self, texts: Union[str, List[str]], model: Optional[str] = None) -> List[List[float]]:
        """
        Generate embeddings for the given text(s).
        
        Args:
            texts: Single text or list of texts to embed
            model: Embedding model to use (defaults to config.embedding_model)
        
        Returns:
            List of embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]
        
        data = {
            "model": model or self.config.embedding_model,
            "input": texts,
            "encoding_format": "float"
        }
        
        try:
            response = self._make_request("/v1/embeddings", data)
            embeddings = [item["embedding"] for item in response["data"]]
            return embeddings
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise
    
    def create_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        Create a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Chat model to use (defaults to config.chat_model)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            Generated text response or full response dict
        """
        data = {
            "model": model or self.config.chat_model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        try:
            response = self._make_request("/v1/chat/completions", data)
            if stream:
                return response
            else:
                return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Failed to create chat completion: {e}")
            raise
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            response = self._make_request("/v1/models", {}, method="GET")
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise


class MistralEmbeddingManager:
    """Manager for Mistral AI embeddings operations."""
    
    def __init__(self, config: Optional[MistralConfig] = None):
        self.client = MistralClient(config)
        self._embedding_cache = {}
    
    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
        
        Returns:
            Embedding vector
        """
        if use_cache and text in self._embedding_cache:
            return self._embedding_cache[text]
        
        embedding = self.client.create_embeddings(text)[0]
        
        if use_cache:
            self._embedding_cache[text] = embedding
        
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process per batch
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.client.create_embeddings(batch)
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Cosine similarity score
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2)
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[tuple[int, float]]:
        """
        Find the most similar embeddings to a query.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return
        
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = [
            (i, self.compute_similarity(query_embedding, candidate))
            for i, candidate in enumerate(candidate_embeddings)
        ]
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]


# Example usage for CodeInsight integration
class MistralRAGClient:
    """RAG-specific client using Mistral AI."""
    
    def __init__(self, config: Optional[MistralConfig] = None):
        self.embedding_manager = MistralEmbeddingManager(config)
        self.client = MistralClient(config)
    
    def generate_with_context(
        self, 
        query: str, 
        context_chunks: List[str], 
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response with RAG context using Mistral AI.
        
        Args:
            query: User query
            context_chunks: Relevant context chunks
            system_prompt: Optional system prompt
        
        Returns:
            Generated response
        """
        if not system_prompt:
            system_prompt = """You are CodeInsight, an AI-powered codebase assistant. 
            You help developers understand code, find relevant documentation, and solve 
            programming problems with up-to-date information from the provided context."""
        
        context = "\n\n".join(context_chunks)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        return self.client.create_chat_completion(messages, temperature=0.7)
