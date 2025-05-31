"""
Prompt Engine Module: Constructs structured prompts for LLM interaction.

Responsibilities:
- Aggregates user query, chat history, and retrieved context.
- Uses a pipeline of components to build system instructions.
- Formats retrieved context and integrates it with the current query.
- Produces a list of messages suitable for LLMService.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional, Union

from pydantic import BaseModel, Field


class PromptBlockContentType(Enum):
    """Defines the type of content a prompt block represents for rendering."""
    HEADING = "heading"         
    PARAGRAPH = "paragraph"    
    BULLET_LIST = "bullet_list"

class PromptBlockOutput(BaseModel):
    """
    Standardized output from each prompt component, guiding final prompt assembly.
    """
    block_id: str
    content_type: PromptBlockContentType
    content: Union[str, List[str]]
    title: Optional[str] = None

    class Config:
        use_enum_values = True # Store enum values as strings


class BasePromptComponent(ABC):
    """
    Abstract base class for all components in the prompt generation pipeline.
    Each component contributes one PromptBlockOutput object.
    """
    def __init__(self, block_id: str):
        self.block_id = block_id

    @abstractmethod
    def execute(
        self,
        current_query: Optional[str] = None,
        retrieved_context: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        existing_system_prompt_parts: Optional[List[PromptBlockOutput]] = None
    ) -> PromptBlockOutput:
        """
        Generates its part of the prompt.
        Returns a single PromptBlockOutput object.
        """
        pass

class BaseBlockRenderer(ABC):
    """Abstract base class for rendering specific content types of PromptBlockOutput."""
    @abstractmethod
    def render(self, content: Union[str, List[str]]) -> str:
        """Renders the given content to a Markdown string."""
        pass

class HeadingBlockRenderer(BaseBlockRenderer):
    """Renders HEADING content type."""
    def render(self, content: Union[str, List[str]]) -> str:
        if isinstance(content, str):
            return f"### {content}\n" # Render HEADING type content as H3
        return "" 

class ParagraphBlockRenderer(BaseBlockRenderer):
    """Renders PARAGRAPH content type."""
    def render(self, content: Union[str, List[str]]) -> str:
        if isinstance(content, list):
            return " ".join(content) + "\n"
        return str(content) + "\n"

class BulletListBlockRenderer(BaseBlockRenderer):
    """Renders BULLET_LIST content type."""
    def render(self, content: Union[str, List[str]]) -> str:
        if isinstance(content, list):
            items_md = [f"- {item}\n" for item in content]
            return "".join(items_md)
        
        return f"- {str(content)}\n"

class RoleDefinitionComponent(BasePromptComponent):
    """Defines the LLM's role."""
    def __init__(self, role_description: str, block_id: str = "role_definition"):
        super().__init__(block_id)
        self.role_description = role_description

    def execute(self, **kwargs) -> PromptBlockOutput:
        return PromptBlockOutput(
            block_id=self.block_id,
            title="LLM Role",
            content_type=PromptBlockContentType.PARAGRAPH,
            content=self.role_description
        )

class PrimaryTaskComponent(BasePromptComponent):
    """Defines the LLM's primary task and objective."""
    def __init__(self, task_description: str, block_id: str = "primary_task"):
        super().__init__(block_id)
        self.task_description = task_description

    def execute(self, **kwargs) -> PromptBlockOutput:
        return PromptBlockOutput(
            block_id=self.block_id,
            title="Primary Task", 
            content_type=PromptBlockContentType.PARAGRAPH,
            content=self.task_description
        )

class ContextUsageRulesComponent(BasePromptComponent):
    """Defines rules for how the LLM should use retrieved context."""
    def __init__(self, rules: List[str], block_id: str = "context_rules"):
        super().__init__(block_id)
        self.rules = rules

    def execute(self, **kwargs) -> PromptBlockOutput:
        return PromptBlockOutput(
            block_id=self.block_id,
            title="Context Usage Rules", 
            content_type=PromptBlockContentType.BULLET_LIST,
            content=self.rules
        )

class InputStructureExplanationComponent(BasePromptComponent):
    """Explains the structure of the input the LLM will receive."""
    def __init__(self, explanations: List[str], block_id: str = "input_structure"):
        super().__init__(block_id)
        self.explanations = explanations

    def execute(self, **kwargs) -> PromptBlockOutput:
        return PromptBlockOutput(
            block_id=self.block_id,
            title="Input Structure", 
            content_type=PromptBlockContentType.BULLET_LIST,
            content=self.explanations
        )

class BasicOutputGuidanceComponent(BasePromptComponent):
    """Provides basic guidance on the desired output style."""
    def __init__(self, guidance_points: List[str], block_id: str = "output_guidance"):
        super().__init__(block_id)
        self.guidance_points = guidance_points

    def execute(self, **kwargs) -> PromptBlockOutput:
        return PromptBlockOutput(
            block_id=self.block_id,
            title="Output Guidance",
            content_type=PromptBlockContentType.BULLET_LIST,
            content=self.guidance_points
        )

class PromptEngine:
    """
    Orchestrates prompt generation using a pipeline of components.
    Renders the final prompt into a list of messages for LLMService.
    """
    def __init__(self, system_prompt_components: List[BasePromptComponent]):
        self.system_prompt_components = system_prompt_components
        self.block_renderers: Dict[PromptBlockContentType, BaseBlockRenderer] = {
            PromptBlockContentType.HEADING: HeadingBlockRenderer(),
            PromptBlockContentType.PARAGRAPH: ParagraphBlockRenderer(),
            PromptBlockContentType.BULLET_LIST: BulletListBlockRenderer(),
        }

    def _render_block_to_markdown(self, block: PromptBlockOutput) -> str:
        """Renders a single PromptBlockOutput to a Markdown string using registered renderers."""
        md_parts = []
        
        # Render the main title for the block (as H2) if it exists
        if block.title:
            md_parts.append(f"## {block.title}\n\n")

        # Get the specific renderer for the content type
        renderer = self.block_renderers.get(block.content_type)
        if renderer:
            md_parts.append(renderer.render(block.content))
        else:
            # Fallback for unknown content type
            md_parts.append(f"[Unsupported content type: {block.content_type}]\n{str(block.content)}\n")
        
        return "".join(md_parts)

    def _build_system_message(
        self,
        current_query: Optional[str] = None,
        retrieved_context: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
        ) -> str:
        """Builds the complete system message string from components."""
        system_prompt_str_parts: List[str] = []

        # For context to later components
        collected_blocks: List[PromptBlockOutput] = [] 

        for component in self.system_prompt_components:
            component_args = {
                "current_query": current_query,
                "retrieved_context": retrieved_context,
                "chat_history": chat_history,
                "existing_system_prompt_parts": collected_blocks.copy()
            }

            # Execute component and get its PromptBlockOutput
            block_output = component.execute(**component_args)
            if block_output:
                collected_blocks.append(block_output)
                system_prompt_str_parts.append(self._render_block_to_markdown(block_output))
        
        return "\n".join(system_prompt_str_parts).strip()


    def _format_retrieved_context(self, context_chunks: List[str]) -> str:
        """Formats a list of context chunks into a single string for the prompt."""
        if not context_chunks:
            return "No relevant context was found for this query."
        
        return "\n---\n".join(context_chunks)
    
    def generate_prompt_messages(
        self,
        current_query: str,
        retrieved_context_chunks: List[str],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Generates the full list of messages for the LLM.
        """
        messages: List[Dict[str, str]] = []

        system_content = self._build_system_message(
            current_query=current_query, 
            retrieved_context=retrieved_context_chunks, 
            chat_history=chat_history
        )
        if system_content:
            messages.append({"role": "system", "content": system_content})

        if chat_history:
            messages.extend(chat_history)
        
        formatted_context = self._format_retrieved_context(retrieved_context_chunks)
        user_message_content = (
            f"User Query: {current_query}\n\n"
            f"Retrieved Context:\n---\n{formatted_context}\n---\n"
            "Based on the context above, please answer the query."
        )
        messages.append({"role": "user", "content": user_message_content})

        return messages

# --- Main execution for demonstration ---
if __name__ == '__main__':
    print("--- PromptEngine Module Demonstration ---")

    # 1. Define concrete components for the system prompt
    role_comp = RoleDefinitionComponent(
        role_description="You are a specialized PLC (Programmable Logic Controller) Technical Assistant and expert, with knowledge of documentation and code samples."
    )
    task_comp = PrimaryTaskComponent(
        task_description="Your primary objective is to accurately answer the user's questions regarding PLCs, their documentation, and related code samples. You must base your answers strictly on the information provided in the 'Retrieved Context' section. Do not use any external knowledge or make assumptions beyond this context."
    )
    context_rules_comp = ContextUsageRulesComponent(
        rules=[
            "The 'Retrieved Context' is your sole source of truth for formulating answers.",
            "If the 'Retrieved Context' does not contain sufficient information to answer the 'User Query', you MUST explicitly state that the information is not available in the provided documents. Do not attempt to answer from outside knowledge or invent information.",
            "If the context contains code samples relevant to the query, present them accurately as found, preserving formatting and indentation if possible within a Markdown code block."
        ]
    )
    input_struct_comp = InputStructureExplanationComponent(
        explanations=[
            "Chat History (if provided): Preceding messages in this conversation will appear first, alternating between 'user' and 'assistant' roles.",
            "User Query: The specific question from the user will be clearly labeled in the final user message.",
            "Retrieved Context: Relevant information fetched from documents (including documentation and code samples) will be provided under a 'Retrieved Context:' heading in the final user message."
        ]
    )
    output_guide_comp = BasicOutputGuidanceComponent(
        guidance_points=[
            "Provide clear, concise, and professional answers.",
            "If the query involves steps or procedures, present them logically.",
            "When providing code examples from the context, use Markdown code blocks for proper formatting (e.g., ```python\n...your code...\n``` or ```\n...your code...\n``` for generic code). Ensure the code is clearly delineated from explanatory text."
        ]
    )

    # 2. Create the PromptEngine with these components
    engine = PromptEngine(
        system_prompt_components=[
            role_comp,
            task_comp,
            context_rules_comp,
            input_struct_comp,
            output_guide_comp
        ]
    )

    # 3. Prepare example inputs
    test_query = "How do I reset a Siemens S7-1200 CPU to factory settings?"
    test_context = [
        "Document A, Page 5: To reset an S7-1200 CPU, ensure the PLC is in STOP mode. Then, navigate to 'Online & Diagnostics', select 'Functions', and choose 'Reset to factory settings'. Acknowledge the warning.",
        "Document B, Section 3.2: Factory reset will erase the user program and hardware configuration. Backup your project first. The process requires TIA Portal."
    ]
    test_history = [
        {"role": "user", "content": "What is a PLC?"},
        {"role": "assistant", "content": "A PLC, or Programmable Logic Controller, is an industrial computer control system..."}
    ]

    # 4. Generate prompt messages
    print("\n--- Generating prompt without chat history ---")
    messages_no_history = engine.generate_prompt_messages(
        current_query=test_query,
        retrieved_context_chunks=test_context
    )
    for msg in messages_no_history:
        print(f"Role: {msg['role']}")
        print(f"Content:\n{msg['content']}\n---")

    print("\n--- Generating prompt with chat history ---")
    messages_with_history = engine.generate_prompt_messages(
        current_query=test_query,
        retrieved_context_chunks=test_context,
        chat_history=test_history
    )
    for msg in messages_with_history:
        print(f"Role: {msg['role']}")
        print(f"Content:\n{msg['content']}\n---")

    print("\n--- Generating prompt with no context provided ---")
    messages_no_context = engine.generate_prompt_messages(
        current_query="What is the weather like?",
        retrieved_context_chunks=[]
    )
    for msg in messages_no_context:
        print(f"Role: {msg['role']}")
        print(f"Content:\n{msg['content']}\n---")

    print("\n--- PromptEngine Module Demonstration Finished ---")