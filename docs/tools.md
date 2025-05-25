# Recommended Tools for PLC RAG Assistant

This document provides a summary of recommended tools and libraries for each layer of the PLC RAG Assistant system. All tools are open-source and can be run locally.

| Layer                | Recommended Tools/Libraries                |
|----------------------|-------------------------------------------|
| User Client (UI)     | Streamlit, Gradio, React.js, Vue.js       |
| Backend App/API      | FastAPI, Flask, LangChain, LlamaIndex     |
| Embeddings           | sentence-transformers, Hugging Face       |
| LLMs                 | Ollama, Text Generation WebUI, HF Transformers |
| Vector DB            | ChromaDB, FAISS                           |
| Chat/User DB         | SQLite, PostgreSQL                        |
| Storage              | Local filesystem, MinIO                   |
| Deployment           | Docker Compose                            |

## Notes

- **User Client (UI):** Streamlit and Gradio are great for rapid prototyping and Python-native development. React.js or Vue.js can be used for more advanced, customizable web UIs.
- **Backend App/API:** FastAPI is modern, async, and integrates well with LangChain or LlamaIndex for RAG orchestration.
- **Embeddings:** Use sentence-transformers for embedding generation. Hugging Face provides a wide range of pre-trained models.
- **LLMs:** Ollama is ideal for running quantized LLMs locally. Text Generation WebUI is more flexible for multi-model setups.
- **Vector DB:** ChromaDB is Python-native and integrates well with LangChain. FAISS is a lightweight alternative for in-memory vector search.
- **Chat/User DB:** SQLite is simple and file-based, suitable for prototyping. PostgreSQL is more robust for multi-user environments.
- **Storage:** Use the local filesystem for simplicity. MinIO is an S3-compatible object storage option if needed.
- **Deployment:** Docker Compose is recommended for orchestrating all services on the university server.
