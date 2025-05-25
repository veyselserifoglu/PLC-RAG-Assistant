# PLC RAG Assistant - System Definition

**Version:** 1.0
**Date:** May 25, 2025

## 1. Introduction

The PLC RAG Assistant is a server-hosted application designed to provide direct assistance to students and programmers working with Programmable Logic Controllers (PLCs). Its primary goal is to enhance productivity and understanding by offering quick, relevant answers and information derived from a comprehensive knowledge base of PLC documentation and code.

The system leverages a Retrieval Augmented Generation (RAG) architecture to deliver accurate and context-aware responses through an accessible web-based chat interface.

## 2. System Objectives

*   **Provide Programming Assistance:** Offer timely and accurate answers to PLC programming queries, including syntax, best practices, troubleshooting, and conceptual explanations.
*   **Centralized Knowledge Access:** Serve as a central repository for PLC-related knowledge, accessible to multiple users.
*   **Personalized Assistance:** Allow users to temporarily augment the system's knowledge base with their own project-specific documents for tailored support during their session.
*   **Ease of Access:** Be accessible via a web browser from standard lab computers within the university network.

## 3. Core Architecture & Components

The PLC RAG Assistant is a client-server application built upon a RAG architecture.

### 3.1. Server-Side Components:

*   **Global Knowledge Base:**
    *   A curated collection of PLC-related documents, including:
        *   Official CODESYS documentation and manuals.
        *   Textual PLC code examples and libraries (e.g., Structured Text, Instruction List) sourced from repositories like GitHub.
    *   Future enhancements will explore methods to incorporate graphical PLC programming languages (e.g., Ladder Logic, Function Block Diagram, Sequential Function Charts).
*   **Data Ingestion & Processing Pipeline:**
    *   **Parsing & Text Extraction:** Scripts and tools to process various document formats (PDFs, HTML, code files).
    *   **Chunking:** Strategies to divide large documents and code into smaller, semantically meaningful segments.
    *   **Embedding Generation:** Utilizes open-source sentence embedding models to convert text chunks into vector representations.
*   **Vector Store:**
    *   A local, server-hosted vector database (e.g., ChromaDB, FAISS) to store and index the embeddings from the global knowledge base and temporary user-uploaded documents.
*   **RAG Orchestration Engine:**
    *   Manages the end-to-end RAG process:
        1.  Receives user queries from the web interface.
        2.  Embeds the user query.
        3.  Retrieves relevant chunks from the vector store (from both global and session-specific knowledge).
        4.  Constructs a comprehensive prompt by combining the original query with the retrieved context.
        5.  Sends the prompt to the LLM for answer generation.
*   **Large Language Model (LLM):**
    *   An open-source, quantized LLM (e.g., Llama 3, Mistral) hosted locally on the university server. Responsible for generating human-like responses based on the augmented prompt.
*   **User Management & Session Control:**
    *   Handles user authentication (login) and manages individual user sessions.
    *   Ensures data isolation for user-uploaded documents, restricting their context to the active session of the uploading user.
    *   Manages conversational memory (history) for each user session to allow for contextual follow-up questions.
*   **Web Server & API:**
    *   Hosts the backend logic and exposes APIs for the client-side interface.

### 3.2. Client-Side Components:

*   **Web-Based Chat Interface:**
    *   Accessible via standard web browsers on lab computers.
    *   Provides a user-friendly interface for:
        *   User login.
        *   Submitting questions to the assistant.
        *   Displaying answers, with clear source attribution where possible.
        *   Uploading project-specific documents for session-based contextualization.
        *   Viewing conversation history.

## 4. Key Features

*   **Natural Language Queries:** Users can ask questions in plain language.
*   **Contextual Answers:** The RAG approach ensures answers are grounded in the provided knowledge base.
*   **Source Attribution:** Where feasible, the system will indicate the source documents or code files used to generate an answer.
*   **Session-Specific Document Upload:** Users can upload documents (e.g., their own PLC project documentation) to receive assistance tailored to their specific context during an active session. This data is temporary and isolated to the user's session.
*   **Conversational Memory:** The assistant remembers the context of the ongoing conversation within a session.
*   **User Authentication:** A basic user creation and login system to manage sessions and user-specific contexts.

## 5. Technical Stack Philosophy

*   **Open Source:** Prioritize the use of open-source tools, libraries, and models for all core components.
*   **Local Deployment:** The entire system, including the LLM and vector database, will be hosted and run on the university's server infrastructure, ensuring data privacy and control.
*   **Modularity:** Designed with modular components to facilitate maintenance, updates, and future enhancements.

## 6. Future Considerations (Out of Scope for Initial Definition)

*   Advanced parsing and representation for graphical PLC languages.
*   Fine-tuning of embedding models or LLMs on PLC-specific corpora.
*   More sophisticated evaluation frameworks for RAG performance.
*   Integration with PLC development environments.
