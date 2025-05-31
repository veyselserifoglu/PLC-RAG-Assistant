"""
Embeddings Module responsibilities:

1. Model Management & Initialization:

- model and provider (e.g., HuggingFace, Ollama, future API).
- Load and initialize the chosen embedding model instance.
- Manage the lifecycle of the model instance (e.g., loading into memory, releasing resources).
- Handle model-specific parameters and authentication (e.g., API keys)

2. Embedding Generation:

- Receive input (a string or a list of strings for document chunks).
- convert input to vector embeddings using the initialized model.
- Handle batching of documents for efficient processing.

3. Output Provision:

- Return the generated embedding vector(s) in a consistent format (e.g., numpy array, list).
- Ensure the output is compatible with downstream applications (e.g., similarity search, clustering).
- Provide a method to retrieve the dimensionality of the embeddings.

4. Resource Management:

- Manage device placement for local models (e.g., CPU/GPU).
- Implement mechanisms for cleaning up resources (e.g., clearing GPU cache, deleting model objects).

"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import gc
import torch
from langchain_community.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings


class EmbeddingModelConfig:
    """
    Configuration for an embedding model provider.
    """
    def __init__(self, provider_type: str, model_identifier: str, **kwargs: Any):
        """
        Args:
            provider_type: Type of provider (e.g., 'huggingface', 'ollama', 'api').
            model_identifier: Name, path, or identifier of the model.
            **kwargs: Additional provider-specific arguments.
        """
        self.provider_type = provider_type.lower()
        self.model_identifier = model_identifier
        self.provider_kwargs = kwargs

class BaseEmbeddingProvider(ABC):
    """
    Abstract base class for all embedding providers.
    """
    def __init__(self, model_identifier: str, **kwargs: Any):
        self.model_identifier = model_identifier
        self.provider_kwargs = kwargs
        self._model: Any = None
        self._dimension: Optional[int] = None

    def load(self) -> None:
        """Loads the embedding model instance if not already loaded."""
        if not self._model:
            self._load_model()
            if not self._model: # Should be set by _load_model
                raise RuntimeError(f"Model '{self.model_identifier}' failed to load.")

    @abstractmethod
    def _load_model(self) -> None:
        """Protected method for concrete classes to load their specific model."""
        pass

    def _ensure_model_loaded(self) -> None:
        """Ensures the model is loaded before use."""
        if not self._model:
            self.load()

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embeds a single text query."""
        self._ensure_model_loaded()
        if not isinstance(text, str):
            raise TypeError("Input 'text' for embed_query must be a string.")

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents."""
        self._ensure_model_loaded()
        if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
            raise TypeError("Input 'texts' for embed_documents must be a list of strings.")

    def cleanup(self) -> None:
        """
        Cleans up resources, e.g., releases model from memory.
        
        TODO: test this within the RAG pipeline (to be modified accordingly).
        """
        if self._model is not None:
            # Generic cleanup
            del self._model
            self._model = None
        
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider for models from Hugging Face."""
    def _load_model(self) -> None:
        if HuggingFaceEmbeddings is None:
            raise ImportError(
                "HuggingFaceEmbeddings (langchain_community) is not installed. "
                "Please install it to use HuggingFaceEmbeddingProvider."
            )

        device = self.provider_kwargs.get("device", "auto")
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        hf_model_kwargs = {'device': device}
        if self.provider_kwargs.get("trust_remote_code"):
            hf_model_kwargs['trust_remote_code'] = True
        
        # Pass through other specific kwargs for HuggingFaceEmbeddings
        for k, v in self.provider_kwargs.items():
            if k not in ['device', 'trust_remote_code', 'normalize_embeddings']:
                 hf_model_kwargs[k] = v
        
        encode_kwargs = {
            'normalize_embeddings': self.provider_kwargs.get(
                "normalize_embeddings", True)}

        self._model = HuggingFaceEmbeddings(
            model_name=self.model_identifier,
            model_kwargs=hf_model_kwargs,
            encode_kwargs=encode_kwargs
        )

    def embed_query(self, text: str) -> List[float]:
        super().embed_query(text)
        return self._model.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        super().embed_documents(texts)
        return self._model.embed_documents(texts)

class EmbeddingService:
    """
    Facade for using embedding providers. Handles batching and provides a consistent interface.
    """
    def __init__(self, provider: BaseEmbeddingProvider, batch_size: int = 32):
        if not isinstance(provider, BaseEmbeddingProvider):
            raise TypeError("Provider must be an instance of BaseEmbeddingProvider.")
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")
            
        self.provider = provider
        self.batch_size = batch_size

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single query using the configured provider."""
        # Input validation is handled by the provider's embed_query method
        return self.provider.embed_query(query)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embeds a list of documents, handling batching if necessary."""
        # Input validation for the list itself
        if not isinstance(documents, list):
            raise TypeError("Input 'documents' must be a list.")
        if not documents: # Handle empty list early
            return []

        if len(documents) <= self.batch_size:
            return self.provider.embed_documents(documents)
        else:
            return self._embed_documents_batched(documents)

    def _embed_documents_batched(self, documents: List[str]) -> List[List[float]]:
        all_embeddings: List[List[float]] = []
        for i in range(0, len(documents), self.batch_size):
            batch_documents = documents[i:i + self.batch_size]
            batch_embeddings = self.provider.embed_documents(batch_documents)
            all_embeddings.extend(batch_embeddings)
            
            # Optional: Aggressive memory clearing for GPU models after each batch
            # TODO: clean up may be needed - must be check within the RAG pipeline.

        return all_embeddings

    def cleanup(self) -> None:
        """Cleans up the underlying embedding provider and its resources."""
        self.provider.cleanup()

    def __enter__(self) -> 'EmbeddingService':
        """Context manager entry."""
        self.provider.load() # Ensure provider's model is loaded when service is entered
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit: ensures cleanup."""
        self.cleanup()

PROVIDER_REGISTRY: Dict[str, type[BaseEmbeddingProvider]] = {
    "huggingface": HuggingFaceEmbeddingProvider
}

def create_embedding_provider(config: EmbeddingModelConfig) -> BaseEmbeddingProvider:
    """
    Factory function to create an instance of an embedding provider.
    Args:
        config: EmbeddingModelConfig object.
    Returns:
        An instance of a BaseEmbeddingProvider.
    """
    if not isinstance(config, EmbeddingModelConfig):
        raise TypeError("config must be an instance of EmbeddingModelConfig.")

    provider_class = PROVIDER_REGISTRY.get(config.provider_type)
    if not provider_class:
        raise ValueError(f"Unsupported provider type: '{config.provider_type}'. "
                         f"Supported types are: {list(PROVIDER_REGISTRY.keys())}")
    
    return provider_class(model_identifier=config.model_identifier, **config.provider_kwargs)

if __name__ == '__main__':
    print("--- Embedding Module Demonstration ---")

    # --- Test HuggingFace Provider (requires sentence-transformers and torch) ---
    print("\nTesting HuggingFace Provider...")
    try:
        # To use a model requiring trust_remote_code:
        hf_config_nomic = EmbeddingModelConfig(
            provider_type="huggingface",
            model_identifier="nomic-ai/nomic-embed-text-v1",
            device="cuda", normalize_embeddings=True, trust_remote_code=True
        )
        hf_provider = create_embedding_provider(hf_config_nomic)
        with EmbeddingService(provider=hf_provider, batch_size=2) as service:
            
            # one string query
            query = "This is a test query for HuggingFace."
            query_emb = service.embed_query(query)
            print(f"HF Query Embedding Dimension: {query_emb[0]}")

            # batch of strings as documents
            docs = ["Doc 1 for HF.", "Doc 2 for HF.", "Doc 3 for HF.", "Doc 4 for HF."]
            doc_embs = service.embed_documents(docs)
            print(f"HF Embedded {len(doc_embs)} documents: {doc_embs[0][0]}")
        print("HuggingFace Provider test completed.")
    except Exception as e:
        print(f"HuggingFace Provider test FAILED: {e}")

    print("\n--- Demonstration Finished ---")
