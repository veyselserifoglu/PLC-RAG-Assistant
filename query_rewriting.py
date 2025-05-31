"""
Query Rewriting Module Responsibilities:

1. Interface for Rewriters (`BaseQueryRewriter`):

- Defines a common abstract interface for various query rewriting techniques.
- Ensures a consistent method for processing a cleaned query.

2. Concrete Rewriter Implementations:

- Provides concrete classes for different rewriting strategies.
- Each class encapsulates the logic for its specific rewriting strategy.

3. Configuration & Instantiation (`QueryRewriterConfig`, `create_query_rewriter`):

- Handles configuration for different rewriter types and their specific parameters.
- Provides a factory mechanism to create specific rewriter instances.

4. Rewriting Service Facade (`QueryRewritingService`):

- Manages an instance of a configured query rewriter.
- Accepts a cleaned query string and optional LLM parameters.
- Delegates the rewriting task to the active rewriter instance.
- Outputs either a single rewritten query string or a list of rewritten query strings.
"""

from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any, Optional, Type
from llm_service import LLMService, GeneratedOutput, LLMProviderConfig, create_llm_provider


class QueryRewriterConfig:
    """
    Configuration for a query rewriter.
    """
    def __init__(self, rewriter_type: str, **kwargs: Any):
        """
        Args:
            rewriter_type: Type of rewriter (e.g., 'passthrough', 'multi_query_llm').
            **kwargs: Rewriter-specific arguments (e.g., num_queries for multi_query,
                      prompt_template, llm_service_instance if pre-configured).
        """
        if not isinstance(rewriter_type, str) or not rewriter_type:
            raise ValueError("rewriter_type must be a non-empty string.")
        
        self.rewriter_type = rewriter_type.lower()
        self.rewriter_kwargs = kwargs

class BaseQueryRewriter(ABC):
    """
    Abstract base class for all query rewriters.
    Defines the contract for rewriting a cleaned query.
    """
    def __init__(self, config: QueryRewriterConfig, llm_service: Optional[LLMService] = None):
        """
        Args:
            config: Configuration specific to this rewriter instance.
            llm_service: An optional LLMService instance, required by LLM-based rewriters.
        """
        self.config = config
        self.llm_service = llm_service # Stored, but only used by LLM-based subclasses

    @abstractmethod
    def rewrite_query(self, cleaned_query: str, 
                      runtime_llm_params: Optional[Dict[str, Any]] = None) -> Union[str, List[str]]:
        """
        Rewrites a cleaned query string.

        Args:
            cleaned_query: The query string after initial preprocessing.
            runtime_llm_params: Optional runtime parameters for LLM-based rewriters
                                (e.g., temperature, max_tokens for this specific call).
                                These might override defaults set via config or in LLMService.
        Returns:
            A single rewritten query string or a list of rewritten query strings.
        """
        if not isinstance(cleaned_query, str):
            raise TypeError("cleaned_query must be a string.")
        if runtime_llm_params is not None and not isinstance(runtime_llm_params, dict):
            raise TypeError("runtime_llm_params must be a dictionary if provided.")

class PassThroughQueryRewriter(BaseQueryRewriter):
    """
    A simple rewriter that performs no transformation.
    It returns the cleaned query as is.
    """
    def __init__(self, config: QueryRewriterConfig, llm_service: Optional[LLMService] = None):
        super().__init__(config, llm_service)
        # This rewriter does not use llm_service, but accepts it for interface consistency.

    def rewrite_query(self, cleaned_query: str, 
                      runtime_llm_params: Optional[Dict[str, Any]] = None) -> Union[str, List[str]]:
        super().rewrite_query(cleaned_query, runtime_llm_params) # Call base for initial checks
        
        return cleaned_query

class LLMMultiQueryRewriter(BaseQueryRewriter):
    """
    An LLM-based rewriter that generates multiple variations of the original query.
    (Placeholder - Not Implemented Yet)
    """
    def __init__(self, config: QueryRewriterConfig, llm_service: Optional[LLMService] = None):
        super().__init__(config, llm_service)
        if not self.llm_service:
            raise ValueError("LLMMultiQueryRewriter requires an LLMService instance.")
        
        # Example: Extract rewriter-specific config
        self.num_queries_to_generate = self.config.rewriter_kwargs.get("num_queries", 3)
        self.prompt_template = self.config.rewriter_kwargs.get(
            "prompt_template",
            "Generate {num_queries} diverse alternative phrasings for the query: '{query}'. "
            "Return each phrasing on a new line."
        )
        print(f"LLMMultiQueryRewriter initialized. Will use LLMService. Num queries: {self.num_queries_to_generate}")


    def rewrite_query(self, cleaned_query: str, runtime_llm_params: Optional[Dict[str, Any]] = None) -> Union[str, List[str]]:
        super().rewrite_query(cleaned_query, runtime_llm_params)
                
        raise NotImplementedError(
            "LLMMultiQueryRewriter.rewrite_query() is not fully implemented yet. "
            "Actual LLM call and response parsing are needed."
        )

class QueryRewritingService:
    """
    Service for applying a chosen query rewriting strategy.
    """
    def __init__(self, rewriter: BaseQueryRewriter):
        """
        Initializes the QueryRewritingService.

        Args:
            rewriter: An instance of a class that implements BaseQueryRewriter.
        """
        if not isinstance(rewriter, BaseQueryRewriter):
            raise TypeError("Rewriter must be an instance of BaseQueryRewriter.")
        self.rewriter = rewriter

    def execute_rewrite(self, cleaned_query: str, 
                        runtime_llm_params: Optional[Dict[str, Any]] = None) -> Union[str, List[str]]:
        """
        Applies the configured rewriting strategy to the cleaned query.

        Args:
            cleaned_query: The query string after initial preprocessing.
            runtime_llm_params: Optional runtime parameters for LLM-based rewriters.

        Returns:
            A single rewritten query string or a list of rewritten query strings.
        """
        return self.rewriter.rewrite_query(cleaned_query, runtime_llm_params=runtime_llm_params)


QUERY_REWRITER_REGISTRY: Dict[str, Type[BaseQueryRewriter]] = {
    "passthrough": PassThroughQueryRewriter,
    "multi_query_llm": LLMMultiQueryRewriter,
}

def create_query_rewriter(
    config: QueryRewriterConfig,
    llm_service: Optional[LLMService] = None
) -> BaseQueryRewriter:
    """
    Factory function to create an instance of a query rewriter.

    Args:
        config: Configuration for the rewriter.
        llm_service: Optional LLMService instance, to be passed to LLM-based rewriters.
    """
    if not isinstance(config, QueryRewriterConfig):
        raise TypeError("config must be an instance of QueryRewriterConfig.")

    rewriter_class = QUERY_REWRITER_REGISTRY.get(config.rewriter_type)
    if not rewriter_class:
        raise ValueError(
            f"Unsupported query rewriter type: '{config.rewriter_type}'. "
            f"Supported types are: {list(QUERY_REWRITER_REGISTRY.keys())}"
        )
    
    return rewriter_class(config, llm_service=llm_service)


if __name__ == '__main__':
    print("--- Query Rewriting Module Demonstration ---")

    sample_cleaned_query = "status of siemens s7-1200 plc"
    print(f"Original Cleaned Query: '{sample_cleaned_query}'")

    # --- Test Case 1: PassThroughQueryRewriter ---
    print("\n--- Test Case 1: PassThrough Rewriter ---")
    passthrough_config = QueryRewriterConfig(rewriter_type="passthrough")
    try:
        passthrough_rewriter_instance = create_query_rewriter(passthrough_config) # No LLMService needed
        rewriting_service_passthrough = QueryRewritingService(rewriter=passthrough_rewriter_instance)
        
        rewritten_output_passthrough = rewriting_service_passthrough.execute_rewrite(sample_cleaned_query)
        print(f"Rewritten (PassThrough): {rewritten_output_passthrough}")
    except Exception as e:
        print(f"PassThrough Rewriter test FAILED: {e}")


    # --- Test Case 2: Invalid Rewriter Type in Factory ---
    print("\n--- Test Case 2: Invalid Rewriter Type in Factory ---")
    invalid_config = QueryRewriterConfig(rewriter_type="non_existent_rewriter")
    try:
        create_query_rewriter(invalid_config)
    except ValueError as e:
        print(f"Caught expected error for invalid rewriter type: {e}")

    print("\n--- Query Rewriting Module Demonstration Finished ---")