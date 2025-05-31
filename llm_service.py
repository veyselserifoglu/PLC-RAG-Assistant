"""
LLMService Module Responsibilities:

1. Abstracted LLM Interaction (BaseLLMProvider):

- Defines a common interface for various LLM providers.
- Supports concrete implementations for specific LLM services.
- LLM Service Facade (LLMService class):

2. Manages an instance of a configured LLM provider.

- Accepts prompts and LLM parameters (e.g., model name, temperature, max tokens).
- Delegates generation tasks to the active LLM provider.

3. Configuration & Instantiation:

- Handles configuration for different LLM providers.
- Provides a mechanism to create specific provider instances.

4. Consistent Result Formatting:

- Ensures LLM-generated output is in a standardized format for downstream use.

5. Resource Management (Basic):

- Manages the lifecycle (e.g., client initialization, potential cleanup).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypedDict, Type
from langchain_ollama import ChatOllama


class LLMProviderConfig:
    """
    Configuration for an LLM provider.
    """
    def __init__(self, provider_type: str, **kwargs: Any):
        """
        Args:
            provider_type: Type of LLM provider (e.g., 'ollama', 'openai', 'placeholder').
            **kwargs: Provider-specific arguments (e.g., model_name, api_key, base_url).
        """
        if not isinstance(provider_type, str) or not provider_type:
            raise ValueError("provider_type must be a non-empty string.")
        
        self.provider_type = provider_type.lower()
        self.provider_kwargs = kwargs
        self.model_name: Optional[str] = kwargs.get("model_name")

class GeneratedOutput(TypedDict):
    """
    Standardized format for LLM-generated output.
    """
    text: str
    model_name: Optional[str] # The model that generated the text
    usage_metadata: Optional[Dict[str, Any]] # e.g., token counts, finish reason
    error: Optional[str] # Error message if generation failed

class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    """
    def __init__(self, config: LLMProviderConfig):
        if not isinstance(config, LLMProviderConfig):
            raise TypeError("config must be an instance of LLMProviderConfig.")
        self.config = config
        self.model_name = config.model_name
        self.llm_client: Any = self._initialize_llm()

    @abstractmethod
    def _initialize_llm(self) -> Any:
        """
        Initializes and returns the underlying LLM client or model object.
        This method is called during provider instantiation.
        """
        pass

    @abstractmethod
    def generate(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> GeneratedOutput:
        """
        Generates text based on a single prompt.

        Args:
            prompt: The input prompt string.
            params: Optional dictionary of runtime parameters for the LLM
                    (e.g., temperature, max_tokens). These might override
                    defaults set during initialization or be specific to the call.

        Returns:
            A GeneratedOutput dictionary.
        """
        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")
        if params is not None and not isinstance(params, dict):
            raise TypeError("params must be a dictionary if provided.")

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None
    ) -> GeneratedOutput:
        """
        Generates a response based on a list of chat messages.
        Each message is a dict with "role" (e.g., "system", "user", "assistant") and "content".

        Args:
            messages: A list of message dictionaries.
            params: Optional dictionary of runtime parameters for the LLM.

        Returns:
            A GeneratedOutput dictionary.
        """
        if not isinstance(messages, list) or not all(
            isinstance(m, dict) and "role" in m and "content" in m for m in messages
        ):
            raise TypeError("messages must be a list of dictionaries, each with 'role' and 'content' keys.")
        if params is not None and not isinstance(params, dict):
            raise TypeError("params must be a dictionary if provided.")
        
        return {
            "text": "",
            "model_name": self.model_name,
            "usage_metadata": None,
            "error": f"{self.__class__.__name__}: is not implemented."
        }

    def cleanup(self) -> None:
        """
        Performs any necessary cleanup for the LLM client (e.g., closing connections).
        Default implementation does nothing.
        """
        self.llm_client = None
        pass

class OllamaLLMProvider(BaseLLMProvider):
    """
    LLM provider for Ollama models using the langchain-ollama package.
    Uses ChatOllama for both generate and chat_completion methods.
    """
    def _initialize_llm(self) -> Any:
        if not self.model_name:
            raise ValueError("model_name must be specified in " \
                        "LLMProviderConfig for OllamaLLMProvider.")

        ollama_params = {
            k: v for k, v in self.config.provider_kwargs.items()
            if k not in ["model_name", "provider_type"]
        }
        try:
            # Using ChatOllama as the client
            chat_model = ChatOllama(model=self.model_name, **ollama_params)
           
            chat_model.invoke([{"role": "user", "content": "Hi"}], config={"max_tokens": 5})
            return chat_model
        
        except Exception as e:
            raise RuntimeError(f"Failed to initialize or" /
                               "connect to Ollama model '{self.model_name}' via ChatOllama: {e}")

    def generate(self, prompt: str, 
                 params: Optional[Dict[str, Any]] = None) -> GeneratedOutput:
        super().generate(prompt, params)
        
        # Adapt the string prompt to the message format expected by ChatOllama
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, params)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None
    ) -> GeneratedOutput:
        super().chat_completion(messages, params) # Base class checks
        if not self.llm_client: # Should have been initialized
             return {
                "text": "", "model_name": self.model_name, "usage_metadata": None,
                "error": "Ollama client not initialized."
            }
        try:
            # Langchain's invoke can take a 'config' dict for runtime parameters
            response_content = self.llm_client.invoke(messages, config=params)
            
            # response_content from ChatOllama is typically AIMessage, we need its content
            text_response = response_content.content if hasattr(response_content, 'content') else str(response_content)

            # Attempt to get usage metadata if available (varies by Langchain version/model)
            usage = None
            if hasattr(response_content, 'response_metadata') and 'token_usage' in response_content.response_metadata:
                usage = response_content.response_metadata['token_usage']
            elif hasattr(response_content, 'usage_metadata'): # Newer Langchain versions
                usage = response_content.usage_metadata

            return {
                "text": text_response,
                "model_name": self.model_name,
                "usage_metadata": usage,
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "model_name": self.model_name,
                "usage_metadata": None,
                "error": f"Ollama chat_completion error: {str(e)}"
            }

class LLMService:
    """
    Facade for using LLM providers. Provides a consistent interface for LLM interactions.
    """
    def __init__(self, provider: BaseLLMProvider):
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError("Provider must be an instance of BaseLLMProvider.")
        self.provider = provider

    def generate_text(self, prompt: str, 
                      params: Optional[Dict[str, Any]] = None) -> GeneratedOutput:
        """
        Generates text using the configured LLM provider's generate method.

        Args:
            prompt: The input prompt string.
            params: Optional dictionary of runtime parameters for the LLM.

        Returns:
            A GeneratedOutput dictionary.
        """
        return self.provider.generate(prompt, params)

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        params: Optional[Dict[str, Any]] = None
    ) -> GeneratedOutput:
        """
        Generates a chat response using the configured LLM provider's chat_completion method.

        Args:
            messages: A list of message dictionaries (e.g., [{"role": "user", "content": "Hello"}]).
            params: Optional dictionary of runtime parameters for the LLM.

        Returns:
            A GeneratedOutput dictionary.
        """
        return self.provider.chat_completion(messages, params)

    def cleanup_provider(self) -> None:
        """Cleans up resources used by the LLM provider, if applicable."""
        self.provider.cleanup()

# --- Provider Registry and Factory ---

LLM_PROVIDER_REGISTRY: Dict[str, Type[BaseLLMProvider]] = {
    "ollama": OllamaLLMProvider,
    # Future providers like "openai": OpenAILLMProvider can be added here
}

def create_llm_provider(config: LLMProviderConfig) -> BaseLLMProvider:
    """
    Factory function to create an instance of an LLM provider.
    """
    if not isinstance(config, LLMProviderConfig):
        raise TypeError("config must be an instance of LLMProviderConfig.")

    provider_class = LLM_PROVIDER_REGISTRY.get(config.provider_type)
    if not provider_class:
        raise ValueError(
            f"Unsupported LLM provider type: '{config.provider_type}'. "
            f"Supported types are: {list(LLM_PROVIDER_REGISTRY.keys())}"
        )
    return provider_class(config)

if __name__ == '__main__':
    print("--- LLMService Module Demonstration (Updated Ollama Provider) ---")

    # --- Test Case 1: OllamaLLMProvider (using ChatOllama) ---
    print("\n--- Test Case 1: OllamaLLMProvider (using ChatOllama) ---")
    
    # Ensure you have Ollama running and the model available.
    ollama_model_name = "gemma3:1b" # Change if you have a different model
    ollama_config = LLMProviderConfig(
        provider_type="ollama",
        model_name=ollama_model_name
    )
    
    try:
        print(f"Attempting to initialize Ollama provider with model '{ollama_model_name}'...")
        print("Ensure Ollama is running, and the model is available")
        ollama_provider = create_llm_provider(ollama_config)
        llm_service_ollama = LLMService(provider=ollama_provider)

        # Test generate() method (which now uses ChatOllama internally)
        prompt2 = "What are the main components of a SCADA system? Answer briefly."
        print(f"\nGenerating text using Ollama (via generate -> ChatOllama) for prompt: '{prompt2}'")
        ollama_runtime_params_gen = {"max_tokens": 150} 
        output2 = llm_service_ollama.generate_text(prompt2, params=ollama_runtime_params_gen)
        
        if output2["error"]:
            print(f"Ollama Generate Error: {output2['error']}")
        else:
            print(f"Ollama Generate Output Text: {output2['text']}")
        print(f"Full Ollama Generate Output: {output2}")

        # Test chat_completion() method
        messages2 = [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Tell me a short joke about computers."}
        ]
        print(f"\nGenerating chat response using Ollama (ChatOllama) for messages: {messages2}")
        ollama_runtime_params_chat = {"temperature": 0.7, "max_tokens": 100}
        chat_output2 = llm_service_ollama.generate_chat_response(messages2, params=ollama_runtime_params_chat)
        
        if chat_output2["error"]:
            print(f"Ollama Chat Error: {chat_output2['error']}")
        else:
            print(f"Ollama Chat Output Text: {chat_output2['text']}")
        print(f"Full Ollama Chat Output: {chat_output2}")


        llm_service_ollama.cleanup_provider()
        print("Ollama provider test completed.")
    except Exception as e:
        print(f"Ollama provider test FAILED with an unexpected error: {e.__class__.__name__}: {e}")

    print("\n--- LLMService Module Demonstration Finished ---")