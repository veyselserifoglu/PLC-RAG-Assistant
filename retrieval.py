"""
Retrieval module resposibilities:

1. Abstracted Vector Store Interaction:

- Defines a common interface (`BaseVectorStoreRetriever`) for various vector databases.
- Supports concrete implementations (e.g., `ChromaDBRetriever`) for specific databases.

2. Retrieval Service Facade (`RetrievalService`):

- Manages an instance of a configured vector store retriever.
- Accepts a query embedding and search parameters (top-k, filters).
- Delegates search operations to the active retriever.

3. Configuration & Instantiation:

- Handles configuration for different vector stores (e.g., paths, collection names, API keys).
- Provides a mechanism (e.g., factory) to create specific retriever instances.

4. Consistent Result Formatting:

- Ensures retrieved data is returned in a standardized format for downstream use in the RAG pipeline.

5. Resource Management:

- Manages the lifecycle (connection, cleanup) of the underlying vector store retriever.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypedDict
import chromadb
from chromadb.api.types import QueryResult

class VectorStoreConfig:
    """
    Configuration for a vector store provider.
    """
    def __init__(self, provider_type: str, **kwargs: Any):
        """
        Args:
            provider_type: Type of provider (e.g., 'chromadb', 'faiss').
            **kwargs: Provider-specific arguments (e.g., path, collection_name for chromadb).
        """
        if not isinstance(provider_type, str) or not provider_type:
            raise ValueError("provider_type must be a non-empty string.")
        
        self.provider_type = provider_type.lower()
        self.provider_kwargs = kwargs

class RetrievedDoc(TypedDict):
    """
    Standardized format for a retrieved document.
    """
    id: str
    content: Optional[str]
    metadata: Optional[Dict[str, Any]]
    score: float # Lower is typically better for distances, higher for similarity

class BaseVectorStoreRetriever(ABC):
    """
    Abstract base class for all vector store retrievers.
    """
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self._is_connected = False

    def connect(self) -> None:
        """Establishes connection or loads the vector store if not already done."""
        if not self._is_connected:
            self._connect_to_store()
            self._is_connected = True

    @abstractmethod
    def _connect_to_store(self) -> None:
        """Protected method for concrete classes to establish connection."""
        pass

    def _ensure_connected(self) -> None:
        """Ensures the store is connected before an operation."""
        if not self._is_connected:
            self.connect()

    @abstractmethod
    def retrieve(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        """
        Retrieves relevant documents from the vector store.
        Args:
            query_embedding: The embedding of the query.
            top_k: The number of top documents to retrieve.
            filters: Optional metadata filters. Format depends on the specific provider.
        Returns:
            A list of RetrievedDoc objects.
        """
        self._ensure_connected()
        if (not isinstance(query_embedding, list) or 
            not all(isinstance(x, float) for x in query_embedding)):
            raise TypeError("query_embedding must be a list of floats.")
        
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")
        
        if filters is not None and not isinstance(filters, dict):
            raise TypeError("filters must be a dictionary if provided.")

    @abstractmethod
    def cleanup(self) -> None:
        """Cleans up resources (e.g., closes connections)."""
        pass

class ChromaDBRetriever(BaseVectorStoreRetriever):
    """
    Vector store retriever for ChromaDB.
    """
    def __init__(self, config: VectorStoreConfig):
        super().__init__(config)

        self.path: Optional[str] = self.config.provider_kwargs.get("path")
        self.collection_name: str = self.config.provider_kwargs.get(
            "collection_name", "default_collection")
        
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[chromadb.api.models.Collection.Collection] = None

    def _connect_to_store(self) -> None:
        """Initializes ChromaDB client and gets/creates the collection."""
        if self.path:
            self.client = chromadb.PersistentClient(path=self.path)
        else:
            self.client = chromadb.Client() # In-memory client

        self.collection = self.client.get_collection(name=self.collection_name)


    def retrieve(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        
        super().retrieve(query_embedding, top_k, filters)
        
        if not self.collection:
            raise RuntimeError("ChromaDB collection is not initialized. Call connect() first.")

        query_results: QueryResult = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters, 
            include=['metadatas', 'documents', 'distances']
        )

        retrieved_docs: List[RetrievedDoc] = []
        # ChromaDB returns lists of lists for batched queries
        # We are sending one query_embedding, so we expect results at index 0.
        ids_list = query_results.get('ids', [[]])[0]
        docs_list = query_results.get('documents', [[]])[0]
        metadatas_list = query_results.get('metadatas', [[]])[0]
        distances_list = query_results.get('distances', [[]])[0] 

        for i in range(len(ids_list)):
            retrieved_docs.append({
                "id": ids_list[i],
                "content": docs_list[i] if docs_list else None,
                "metadata": metadatas_list[i] if metadatas_list else None,
                "score": distances_list[i] if distances_list else float('inf')
            })
        return retrieved_docs

    def cleanup(self) -> None:
        """
        ChromaDB client might not have an explicit close. Resetting references.
        TODO: test this within the RAG pipeline (to be modified accordingly).
        """
        self.collection = None
        self.client = None # Allow garbage collection if persistent client is not shared
        self._is_connected = False


class RetrievalService:
    """
    Facade for using vector store retrievers.
    """
    def __init__(self, retriever: BaseVectorStoreRetriever):
        if not isinstance(retriever, BaseVectorStoreRetriever):
            raise TypeError("Retriever must be an instance of BaseVectorStoreRetriever.")
        self.retriever = retriever

    def retrieve_documents(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDoc]:
        """
        Retrieves documents using the configured retriever.
        """
        return self.retriever.retrieve(query_embedding, top_k, filters)

    def __enter__(self) -> 'RetrievalService':
        """Context manager entry: connects the retriever."""
        self.retriever.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit: cleans up the retriever."""
        self.retriever.cleanup()

PROVIDER_REGISTRY: Dict[str, type[BaseVectorStoreRetriever]] = {
    "chromadb": ChromaDBRetriever
    # Future providers like "faiss": FAISSRetriever can be added here
}

def create_retriever(config: VectorStoreConfig) -> BaseVectorStoreRetriever:
    """
    Factory function to create an instance of a vector store retriever.
    """
    if not isinstance(config, VectorStoreConfig):
        raise TypeError("config must be an instance of VectorStoreConfig.")

    retriever_class = PROVIDER_REGISTRY.get(config.provider_type)
    if not retriever_class:
        raise ValueError(f"Unsupported retriever provider type: '{config.provider_type}'. "
                         f"Supported types are: {list(PROVIDER_REGISTRY.keys())}")
    return retriever_class(config)


if __name__ == '__main__':
    print("--- Retrieval Module Demonstration ---")

    # --- Test ChromaDBRetriever ---
    # This test assumes ChromaDB is installed.
    # For a real scenario, documents would be added in a separate indexing pipeline.
    # Here, we'll add a few dummy documents for demonstration.
    print("\nTesting ChromaDBRetriever...")

    collection_name_for_test = "test_plc_docs_main"
    chroma_db_path_for_test = "./chroma_db_test_main"

    test_setup_client = chromadb.PersistentClient(path=chroma_db_path_for_test)

    print(f"Ensuring ChromaDB collection '{collection_name_for_test}' exists...")
    test_collection = test_setup_client.get_or_create_collection(name=collection_name_for_test)
            
    # Configuration for an in-memory ChromaDB for this test
    chroma_config = VectorStoreConfig(
        provider_type="chromadb",
        path=chroma_db_path_for_test,
        collection_name=collection_name_for_test
    )
    retriever_instance = create_retriever(chroma_config)

    try:
        with RetrievalService(retriever_instance) as service: 
           
            print(f"Populating ChromaDB collection '{service.retriever.collection_name}' for test...")
            try:
                service.retriever.collection.add(
                    ids=["doc1", "doc2", "doc3", "doc4"],
                    embeddings=[
                        [0.1, 0.2, 0.3], [0.4, 0.5, 0.6], # Dummy embeddings
                        [0.7, 0.8, 0.9], [0.2, 0.3, 0.1]
                    ],
                    metadatas=[
                        {"source": "manual_a", "type": "faq"},
                        {"source": "manual_b", "type": "guide"},
                        {"source": "manual_a", "type": "troubleshooting"},
                        {"source": "manual_c", "type": "faq"}
                    ],
                    documents=[
                        "PLC programming basics and introduction.",
                        "Advanced control logic for PLCs.",
                        "Troubleshooting common PLC errors.",
                        "Frequently asked questions about PLC setup."
                    ]
                )
                print("Dummy data added to ChromaDB.")
            except Exception as add_e: 
                print(f"Note: Could not add dummy data: {add_e}")

            # Dummy query embedding (should match the dimension of stored embeddings)
            dummy_query_embedding = [0.15, 0.25, 0.35]

            print(f"\nRetrieving top 2 documents for query_embedding: {dummy_query_embedding}")
            retrieved_docs = service.retrieve_documents(dummy_query_embedding, top_k=2)
            for doc in retrieved_docs:
                print(f"ID: {doc['id']}, Score: {doc['score']:.4f}, Content: '{doc.get('content', '')[:30]}...'")
                print(f"Metadata: {doc['metadata']}")

            print(f"\nRetrieving top 1 document with filter {{'source': 'manual_b'}}")
            filtered_docs = service.retrieve_documents(
                dummy_query_embedding,
                top_k=1,
                filters={"source": "manual_b"}
            )
            for doc in filtered_docs:
                print(f"ID: {doc['id']}, Score: {doc['score']:.4f}, Content: '{doc.get('content', '')[:30]}...'")
                print(f"Metadata: {doc['metadata']}")

        print("ChromaDBRetriever test completed.")
    except Exception as e:
        print(f"ChromaDBRetriever test FAILED: {e}")

print("\n--- Retrieval Module Demonstration Finished ---")