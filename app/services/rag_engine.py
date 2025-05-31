"""
Core RAG Query Orchestrator / Pipeline Manager:

Responsibilities: This is the central "brain" that manages the flow of a user's query through all the other modules.
Receives the raw user query.
Calls the Preprocessing Module for the query.
Calls the EmbeddingModule to get the query embedding.
Calls the RetrievalModule to fetch initial candidate documents.
Calls the RerankModule to refine the candidate list.
Passes the refined context to the next stage (Context Compilation).
Why it's needed: To coordinate the sequence of operations for handling an incoming query.

"""