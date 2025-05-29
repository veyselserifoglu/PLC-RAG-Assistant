# Phase 1 Prototype: Feature Breakdown

This document outlines the features for the initial prototype of the PLC RAG Assistant, divided into MCP Server and MCP Client components.

## I. Minimal Viable RAG Core (MCP Server)

### 1. Feature: Basic MCP Server Endpoint Setup
*   **Description:** Create a FastAPI application with a single POST endpoint (e.g., `/query`) that accepts a JSON payload containing the user's raw query string.
*   **Tasks:**
    *   Set up FastAPI project structure.
    *   Define Pydantic model for the request body.
    *   Implement the basic endpoint that initially returns a dummy response.
*   **Estimate:** 0.5 - 1 day
*   **Dependencies:** None

### 2. Feature: Pre-loaded In-Memory Vector Store
*   **Description:** Manually prepare 5-10 sample PLC text chunks. Implement logic to embed these chunks using a chosen sentence transformer model and load them into an in-memory FAISS (or ChromaDB) index when the server starts.
*   **Tasks:**
    *   Select and prepare sample text data.
    *   Write a utility script/function to:
        *   Load a sentence transformer model.
        *   Embed the text chunks.
        *   Create and populate a FAISS index.
    *   Integrate this loading process into the server's startup sequence.
*   **Estimate:** 1 - 1.5 days
*   **Dependencies:** Choice of embedding model.

### 3. Feature: Basic Vector DB Retrieval
*   **Description:** Implement the logic within the `/query` endpoint to take the incoming raw query, embed it using the same sentence transformer model, and perform a similarity search against the pre-loaded FAISS index to retrieve the top K relevant chunks.
*   **Tasks:**
    *   Load the sentence transformer model in the endpoint context (or globally).
    *   Embed the incoming query.
    *   Perform FAISS search.
*   **Estimate:** 0.5 - 1 day
*   **Dependencies:** Feature 2 (Pre-loaded Vector Store)

### 4. Feature: Basic Prompt Augmentation & LLM Call
*   **Description:** Take the retrieved chunks and the original query, format them into a simple prompt. Implement logic to call the locally running Ollama LLM service with this augmented prompt.
*   **Tasks:**
    *   Define a simple prompt template.
    *   Concatenate query and retrieved chunks into the prompt.
    *   Use the `ollama` library to send the prompt to the LLM and get the response.
*   **Estimate:** 0.5 - 1 day
*   **Dependencies:** Feature 3 (Basic Vector DB Retrieval), Ollama service running.

### 5. Feature: Return LLM Output via MCP Endpoint
*   **Description:** Modify the `/query` endpoint to return the LLM's generated text as a JSON response.
*   **Tasks:**
    *   Define Pydantic model for the response body.
    *   Return the LLM output.
*   **Estimate:** 0.25 days
*   **Dependencies:** Feature 4 (LLM Call)

## II. Minimal Viable MCP Client

### 1. Feature: Simple Query Client (Python Script)
*   **Description:** Create a command-line Python script that:
    *   Takes a query string as input from the user.
    *   Sends an HTTP POST request to the MCP server's `/query` endpoint with the query.
    *   Prints the server's JSON response (the LLM's generated text).
*   **Tasks:**
    *   Use the `requests` library.
    *   Handle user input and basic error checking for the request.
*   **Estimate:** 0.5 - 1 day
*   **Dependencies:** A running MCP Server (can be mocked initially for client development).
