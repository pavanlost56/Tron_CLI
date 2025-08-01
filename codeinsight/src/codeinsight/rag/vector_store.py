"""Vector store for code embeddings using ChromaDB."""
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from ..core.config import settings as app_settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage vector storage for code embeddings."""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """Initialize vector store."""
        self.persist_directory = persist_directory or app_settings.vector_db_path
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=app_settings.embedding_model
        )
        
        # Get or create collection
        self.collection_name = "codeinsight_codebase"
        self._init_collection()
    
    def _init_collection(self):
        """Initialize or get existing collection."""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def add_code_snippet(
        self,
        code: str,
        metadata: Dict[str, Any],
        snippet_id: Optional[str] = None
    ) -> str:
        """Add a code snippet to the vector store."""
        try:
            # Generate ID if not provided
            if not snippet_id:
                import hashlib
                snippet_id = hashlib.md5(code.encode()).hexdigest()
            
            # Add to collection
            self.collection.add(
                documents=[code],
                metadatas=[metadata],
                ids=[snippet_id]
            )
            
            logger.debug(f"Added snippet {snippet_id} to vector store")
            return snippet_id
        except Exception as e:
            logger.error(f"Error adding code snippet: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar code snippets."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return {
                'query': query,
                'results': formatted_results,
                'count': len(formatted_results)
            }
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def delete_by_file(self, file_path: str):
        """Delete all snippets from a specific file."""
        try:
            self.collection.delete(
                where={"file_path": file_path}
            )
            logger.info(f"Deleted snippets from file: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting snippets: {e}")
            raise
    
    def update_snippet(
        self,
        snippet_id: str,
        code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update an existing code snippet."""
        try:
            update_args = {"ids": [snippet_id]}
            
            if code:
                update_args["documents"] = [code]
            if metadata:
                update_args["metadatas"] = [metadata]
            
            self.collection.update(**update_args)
            logger.debug(f"Updated snippet {snippet_id}")
        except Exception as e:
            logger.error(f"Error updating snippet: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            count = self.collection.count()
            return {
                'total_snippets': count,
                'collection_name': self.collection_name,
                'persist_directory': str(self.persist_directory)
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise
    
    def clear(self):
        """Clear all data from the vector store."""
        try:
            self.client.delete_collection(self.collection_name)
            self._init_collection()
            logger.info("Cleared vector store")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
