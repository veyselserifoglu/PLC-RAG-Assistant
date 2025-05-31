# Implemented RAG Core Features

This document outlines the core features that form the foundation of the RAG pipeline.

## - [x] 1. Feature: Query Preprocessing (`query_preprocessing.py`)
*   **Description:** Standardizes and refines the raw user query to improve its suitability for downstream processing.
*   **Responsibilities:**
    *   Performs basic cleaning operations such as lowercasing, stripping leading/trailing whitespace, and removing redundant characters.
    *   Can implement more advanced steps like spell correction or stop-word removal based on defined strategies.

## - [x] 2. Feature: Query Rewriting (`query_rewriting.py`)
*   **Description:** Transforms the user's query into one or more optimized versions better suited for semantic retrieval from the knowledge base.
*   **Responsibilities:**
    *   Generates alternative phrasings or expands the query with synonyms and related terms to cover different aspects of the user's intent.
    *   Adapts the query to better match the language and terminology used in the knowledge base documents and code samples.

## - [x] 3. Feature: Embedding Generation Service (`embeddings.py`)
*   **Description:** Provides a consistent interface for converting text (queries and document chunks) into dense vector representations (embeddings).
*   **Responsibilities:**
    *   Loads and manages various sentence transformer models or other embedding providers.
    *   Offers methods to embed single queries and batches of documents, returning their vector representations.

## - [x] 4. Feature: Context Retrieval (`retrieval.py`)
*   **Description:** Fetches relevant document chunks from a specialized vector database based on the semantic similarity of their embeddings to the query embedding.
*   **Responsibilities:**
    *   Interfaces with a vector store (e.g., FAISS, ChromaDB) to perform similarity searches.
    *   Retrieves the top-K most relevant document chunks (text and metadata) corresponding to the user's query.

## - [x] 5. Feature: Dynamic Prompt Construction Engine (`prompt_engine.py`)
*   **Description:** Dynamically assembles detailed and structured prompts for the LLM, incorporating system instructions, chat history, the user's query, and retrieved context.
*   **Responsibilities:**
    *   Utilizes a pipeline of configurable components to build a comprehensive system message, including LLM role, task definition, context usage rules, and output formatting guidelines, rendered to Markdown.
    *   Integrates chat history and the current user query with the formatted retrieved context to produce a final list of messages suitable for the LLM service.

---
# TODO RAG Features

## - [ ] 6. Feature: FastAPI Server & API Endpoint
*   **Description:** The web server application that will expose the RAG functionality via an API endpoint.
*   **Responsibilities:**
    *   Set up a FastAPI application.
    *   Define an API endpoint (e.g., /chat or /answer) that accepts user queries and optionally session information.
    *   Handle incoming requests, call the RAG engine orchestrator, and return the processed response.

## - [ ] 7. Feature: Application-Level Configuration Management
*   **Description:** A system for managing all necessary configurations for the application, including services like LLMService, EmbeddingService, VectorStoreService, and database connections.
*   **Responsibilities:**
    *   Define a structure for a main configuration file (e.g., config.yaml or using environment variables) to hold settings like model names, API endpoints, file paths, database connection strings, etc.
    *   Implement logic to load and provide access to these configurations throughout the application.

## - [ ] 8. Feature: Prompt Configuration Loading System
*   **Description:** Mechanism to load instructional texts for PromptEngine components from an external configuration file.
*   **Responsibilities:**
    *   Define the structure of the prompt_config.yaml file.
    *   Implement logic (likely at application startup) to parse this YAML file and use its content to instantiate and configure the various BasePromptComponent instances (e.g., RoleDefinitionComponent, ContextUsageRulesComponent).

## - [ ] 9. Feature: Chat History Management & Persistence
*   **Description:** System for storing, retrieving, and updating conversation histories.
*   **Responsibilities:**
    *   Design and set up a database schema (e.g., in SQLite or another SQL database) to store chat messages, associating them with user sessions.
    *   Implement functions/methods to fetch a specified number of recent chat turns for a given session and to save new user queries and LLM responses to the history.

## - [ ] 10. Feature: Response Post-processing Module
*   **Description:** A dedicated module or function to refine the raw output from the LLM before it's presented to the user.
*   **Responsibilities:**
    *   Implement logic to clean up LLM responses (e.g., remove extraneous conversational fillers, ensure consistent formatting).
    *   Potentially handle extraction of specific information if the LLM is prompted to provide structured output elements (though this might be more advanced for Phase 1).

## - [ ] 11. Feature: Data Ingestion Pipeline/Script
*   **Description:** A process or script to load the knowledge base (PLC documentation and code samples), process it, generate embeddings, and populate the vector store.
*   **Responsibilities:**
    *   Utilize data_loader.py to load documents.
    *   Use text_splitter.py to chunk documents.
    *   Employ embedding_service.py to generate embeddings for the chunks.
    *   Use vector_store_service.py to add these embeddings and their corresponding text chunks to the persistent vector database. (This is a prerequisite setup, not part of the live query flow).

## - [ ] 12. Feature: RAG Engine Orchestrator
*   **Description:** The central component that coordinates the entire RAG pipeline, from receiving a user query to returning a final answer.
*   **Responsibilities:**
    *   Manages instances of all necessary services (Embedding, Vector Store, Prompt Engine, LLM Service, Chat History, etc.).
    *   Executes the sequence of RAG operations: query processing, embedding, retrieval, prompt construction, LLM interaction, and response post-processing.