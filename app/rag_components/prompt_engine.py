"""
Simple Prompt Formatter Module: Simplified approach for prompt generation.

Responsibilities:
- Provides a registry-based system for different prompt strategies.
- Formats chat history, retrieved context, and user queries into a single prompt string.
- Uses template-based approach with placeholder substitution.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Type

class BasePromptComponent(ABC):
    """Abstract base class for prompt generation components."""
    
    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template
    
    @abstractmethod
    def execute(
        self,
        current_query: str,
        retrieved_context_chunks: List[str],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a complete prompt string.
        
        Args:
            current_query: The user's current question
            retrieved_context_chunks: List of retrieved context strings
            chat_history: Optional list of chat turns [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Complete formatted prompt string
        """
        pass

class GeneralUsePrompt(BasePromptComponent):
    """General purpose prompt formatter for PLC assistant."""
    
    def execute(
        self,
        current_query: str,
        retrieved_context_chunks: List[str],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate formatted prompt string with all components."""
        
        # Format chat history
        formatted_chat_history = self._format_chat_history(chat_history)
        
        # Format retrieved context
        formatted_context = self._format_retrieved_context(retrieved_context_chunks)
        
        # Fill template placeholders
        formatted_prompt = self.prompt_template.format(
            chat_history=formatted_chat_history,
            user_query=current_query,
            retrieved_context=formatted_context
        )
        
        return formatted_prompt
    
    def _format_chat_history(self, chat_history: Optional[List[Dict[str, str]]]) -> str:
        """Format chat history into a string."""
        if not chat_history:
            return "No prior conversation history."
        
        formatted_turns = []
        for turn in chat_history:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            formatted_turns.append(f"{role}: {content}")
        
        return "\n".join(formatted_turns)
    
    def _format_retrieved_context(self, context_chunks: List[str]) -> str:
        """Format retrieved context chunks into a string."""
        if not context_chunks:
            return "No relevant context found."
        
        return "\n---\n".join(context_chunks)

# Registry of prompt providers - similar to retrieval.py pattern
PROMPT_PROVIDER_REGISTRY: Dict[str, Type[BasePromptComponent]] = {
    "general_use": GeneralUsePrompt
}

def create_prompt_formatter(prompt_type: str, prompt_template: str) -> BasePromptComponent:
    """
    Factory function to create an instance of a prompt formatter.
    
    Args:
        prompt_type: The type of prompt formatter to use.
        prompt_template: The template string to use for prompt generation
        
    Returns:
        An instance of the specified prompt formatter
    """
    formatter_class = PROMPT_PROVIDER_REGISTRY.get(prompt_type)
    if not formatter_class:
        raise ValueError(f"Unsupported prompt formatter type: '{prompt_type}'. "
                         f"Supported types are: {list(PROMPT_PROVIDER_REGISTRY.keys())}")
    return formatter_class(prompt_template=prompt_template)

# Demo usage
if __name__ == "__main__":
    from app.core.config import settings
    
    print("--- Simple Prompt Formatter Demonstration ---")
    
    # Get prompt template from config
    prompt_template = settings.prompt_config.general_system_template
    
    # Create prompt formatter using the factory function
    prompt_formatter = create_prompt_formatter(
        prompt_type="general_use",
        prompt_template=prompt_template
    )
    
    # Test data
    test_query = "What is a PLC and how does it work?"
    test_context = [
        "A PLC (Programmable Logic Controller) is an industrial computer used to control manufacturing processes.",
        "PLCs use ladder logic programming and can interface with various sensors and actuators."
    ]
    test_history = [
        {"role": "user", "content": "Tell me about industrial automation."},
        {"role": "assistant", "content": "Industrial automation involves using control systems like PLCs to operate equipment."}
    ]
    
    # Generate prompt
    generated_prompt = prompt_formatter.execute(
        current_query=test_query,
        retrieved_context_chunks=test_context,
        chat_history=test_history
    )
    
    print("Generated Prompt:")
    print("=" * 80)
    print(generated_prompt)
    print("=" * 80)
    
    # Test with no history/context
    print("\nTesting with minimal data:")
    minimal_prompt = prompt_formatter.execute(
        current_query="What is ladder logic?",
        retrieved_context_chunks=[],
        chat_history=None
    )
    print("Minimal prompt snippet:")
    print(minimal_prompt[:200] + "...")