"""
Query Preprocessing Module:

Primary Responsibilities:

1. Initial Query Cleaning & Normalization:

- Accepts a raw user query string.
- Performs basic cleaning (e.g., noise reduction).
- Outputs a standardized, cleaned query string.

2. LLM-based Denoising (Optional):

- For heavily noisy or unstructured queries, use LLM to extract the core intent of the query.
- This would be a configurable step.

3. Preparation for Rewriting:

- Ensures the cleaned query is in a suitable format to be passed downstream.

Note: This module focuses *only* on the initial processing of the query string.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import re
import html
from llm_service import LLMService
from bs4 import BeautifulSoup


class BaseQueryProcessor(ABC):
    """Abstract base class for a query processing step."""
    @abstractmethod
    def process(self, query: str) -> str:
        """Processes the query string and returns the processed version."""
        pass

class BaseLLMQueryDenoiser(ABC):
    """
    Abstract base class for an LLM-based query denoiser.
    """
    @abstractmethod
    def denoise(self, query: str, task_specific_llm_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Uses an LLM to denoise or extract intent from a noisy query.
        Args:
            query: The noisy query string.
            task_specific_llm_params: Optional parameters specific to this denoising task
                                      (e.g., temperature, max_tokens for this specific call).
        Returns:
            A cleaned or rephrased query string.
        """
        pass

class WhitespaceNormalizer(BaseQueryProcessor):
    """Normalizes whitespace in a query."""
    def process(self, query: str) -> str:
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")
        query = query.strip()
        query = re.sub(r'\s+', ' ', query)
        return query

class HTMLCleaner(BaseQueryProcessor):
    """Removes HTML tags and unescapes HTML entities."""
    def __init__(self, use_robust_parser: bool = False):
        self.use_robust_parser = use_robust_parser
        self._beautifulsoup_available = False
        if self.use_robust_parser:
            self.BeautifulSoup = BeautifulSoup
            self._beautifulsoup_available = True

    def process(self, query: str) -> str:
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")
        
        processed_query: str
        if self.use_robust_parser and self._beautifulsoup_available:
            soup = self.BeautifulSoup(query, "html.parser")
            processed_query = soup.get_text(separator=' ')
        else:
            processed_query = re.sub(r'<[^>]+>', '', query)

        processed_query = html.unescape(processed_query)
        return processed_query

class LLMQueryDenoiser(BaseLLMQueryDenoiser):
    """
    An LLM-based query denoiser that uses the LLMService.
    """
    def __init__(self, llm_service: LLMService, 
                 default_prompt_template: Optional[str] = None):
        if not isinstance(llm_service, LLMService):
            raise TypeError("llm_service must be an instance of LLMService.")
        self.llm_service = llm_service
        self.default_prompt_template = default_prompt_template

    def denoise(self, query: str, 
                task_specific_llm_params: Optional[Dict[str, Any]] = None) -> str:
        if not isinstance(query, str):
            raise TypeError("Query to denoise must be a string.")

        return NotImplementedError

class QueryPreprocessingService:
    """
    Service for cleaning and normalizing user queries.
    """
    def __init__(
        self,
        basic_processors: Optional[List[BaseQueryProcessor]] = None,
        llm_denoiser: Optional[BaseLLMQueryDenoiser] = None,
        use_llm_denoiser_flag: bool = False
    ):
        if basic_processors is None:
            self.basic_processors: List[BaseQueryProcessor] = [
                HTMLCleaner(),
                WhitespaceNormalizer()
            ]
        elif all(isinstance(p, BaseQueryProcessor) for p in basic_processors):
            self.basic_processors = basic_processors
        else:
            raise TypeError("All items in basic_processors must " \
                            "be instances of BaseQueryProcessor.")

        if llm_denoiser is not None and not isinstance(llm_denoiser, BaseLLMQueryDenoiser):
            raise TypeError("llm_denoiser must be an instance of BaseLLMQueryDenoiser or None.")
        
        self.llm_denoiser = llm_denoiser
        self.use_llm_denoiser_flag = use_llm_denoiser_flag

    def preprocess_query(
            self, raw_query: str, 
            task_specific_llm_params: Optional[Dict[str, Any]] = None) -> str:
        if not isinstance(raw_query, str):
            raise TypeError("Raw query must be a string.")

        processed_query = raw_query
        for processor in self.basic_processors:
            processed_query = processor.process(processed_query)

        if self.use_llm_denoiser_flag and self.llm_denoiser:
            processed_query = self.llm_denoiser.denoise(
                    processed_query, 
                    task_specific_llm_params=task_specific_llm_params
                )
        
        # Ensure clean whitespace at the very end
        final_normalizer = WhitespaceNormalizer()
        processed_query = final_normalizer.process(processed_query)
        
        return processed_query

if __name__ == '__main__':
    print("--- Query Preprocessing Module Demonstration (with LLMService integration) ---")

    # --- Test Case 1: Basic Cleaning ---
    print("\n--- Test Case 1: Basic Cleaning (Defaults) ---")
    raw_query1 = "  <p>what is   the status of   <strong>project &amp; development</strong>?</p>  "
    print(f"Raw Query 1: '{raw_query1}'")
    preprocessor_default = QueryPreprocessingService() # No LLM denoiser by default
    clean_query1 = preprocessor_default.preprocess_query(raw_query1)
    print(f"Cleaned Query 1: '{clean_query1}'")

    # --- Test Case 2: With LLM Denoising Enabled (using LLMQueryDenoiser with Placeholder LLMService) ---
    print("\n--- Test Case 2: With LLM Denoising ---")
    raw_query2 = "  user typed this vry fast & w/ errors, like <br> need plc info for siemens s7 1200 blinking led status thx  "
    print(f"Raw Query 2: '{raw_query2}'")
    
    # --- Test Case 3: Robust HTML Cleaning ---
    print("\n--- Test Case 3: Robust HTML Cleaning ---")
    preprocessor_robust_html = QueryPreprocessingService(
        basic_processors=[HTMLCleaner(use_robust_parser=True), WhitespaceNormalizer()]
    )
    clean_query4_robust = preprocessor_robust_html.preprocess_query(raw_query1)
    print(f"Cleaned Query 1 (Robust HTML): '{clean_query4_robust}'")


    print("\n--- Query Preprocessing Module Demonstration Finished ---")