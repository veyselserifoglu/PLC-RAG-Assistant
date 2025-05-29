```markdown
# RAG System Architecture and Data Flow

This document provides a comprehensive overview of the architecture and data flow for the Retrieval-Augmented Generation (RAG) system. The diagrams illustrate the various components and their interactions within the system.

## 1. System Architecture Overview

```mermaid
graph TD
    subgraph "User Client"
        Client[Web Browser]
    end

    subgraph "University Server Infrastructure"
        direction TB

        subgraph "Backend Application"
            AppServer["App Logic (Python/LangChain/FastAPI)"]
            AppServer -- "uses" --> LLMTool["LLMs (Ollama)"]
            AppServer -- "uses" --> EmbeddingTool["Embeddings (SentenceTrans)"]
        end
        
        subgraph "Databases"
            VectorDB["Vector DB (ChromaDB)"]
            ChatHistoryDB["Chat History (SQLite)"]
        end

        subgraph "Persistent Storage (Source Data for Vector DB Ingestion)"
            GlobalKB[("Global KB: CODESYS Docs, Code")]
            TempDocs[("Temp User Docs")]
        end
    end

    Client --> AppServer

    AppServer -- "Retrieves Embeddings" --> VectorDB
    AppServer -- "Reads/Writes Chat History" --> ChatHistoryDB
    
    %% VectorDB ingestion flow (conceptual, not real-time query path)
    GlobalKB -.-> VectorDB
    TempDocs -.-> VectorDB

    classDef client fill:#ccf,stroke:#333,stroke-width:2px;
    classDef backendApp fill:#f9f,stroke:#333,stroke-width:2px;
    classDef tool fill:#e6e6fa,stroke:#333,stroke-width:2px;
    classDef database fill:#bbf,stroke:#333,stroke-width:2px;
    classDef storage fill:#lightgrey,stroke:#333,stroke-width:2px;

    class Client client;
    class AppServer backendApp;
    class LLMTool,EmbeddingTool tool;
    class VectorDB,ChatHistoryDB database;
    class GlobalKB,TempDocs storage;
```

### 2. Data Flow Diagram - Main RAG Query Processing

```mermaid
graph TD
    subgraph "User"
    A[Enters Query] --> M[Sees Response]
    end
    
    subgraph "Web Layer"
    B[Server] --> C[Auth]
    K[Server] --> L[UI]
    end
    
    subgraph "RAG System"
    D[Core] --> E[Embed]
    E --> F[Search]
    F --> G[Retrieve]
    end
    
    A --> B
    C --> D
    G --> H[Augment]
    H --> I[LLM]
    I --> J[Gen Response]
    J --> K
```

### 3. Deployment Diagram (Docker Focus)

```mermaid
graph TD
    subgraph "Lab Computers"
        User1["User Web Browser"]
        User2["User Web Browser"]
        UserN["User Web Browser"]
    end

    subgraph "University Server (Host Machine)"
        direction TB
        
        subgraph "Web Layer"
            OpenWebUI["OpenWebUI Container
            - User Interface
            - Auth Gateway"]
        end

        subgraph "Application Layer"
            RAGCore["RAG Core Service
            - Query Processing
            - Prompt Engineering"]
            
            EmbeddingService["Embedding Service
            (Local Model)"]
        end

        subgraph "Database Layer"
            VectorDB["Vector DB (ChromaDB/FAISS)
            - Global Knowledge Base"]
            
            PostgresDB["PostgreSQL
            - Chat History
            - User Sessions"]
        end

        subgraph "LLM Layer"
            LocalLLM["LLM Container
            (Ollama + Llama3)"]
        end

        VolumeKB["Volume: Knowledge Base"]
        VolumeChat["Volume: Chat History"]
    end

    %% Connections
    User1 --> OpenWebUI
    User2 --> OpenWebUI
    UserN --> OpenWebUI

    OpenWebUI --> RAGCore
    RAGCore --> EmbeddingService
    RAGCore --> VectorDB
    RAGCore --> PostgresDB
    RAGCore --> LocalLLM

    EmbeddingService --> VectorDB
    VectorDB -- "mounts" --> VolumeKB
    PostgresDB -- "mounts" --> VolumeChat

    classDef user fill:#ccf,stroke:#333
    classDef web fill:#cff,stroke:#333
    classDef app fill:#bbf,stroke:#333
    classDef db fill:#fbf,stroke:#333
    classDef llm fill:#cfc,stroke:#333
    classDef volume fill:#eee,stroke-dasharray:3 3,stroke:#333

    class User1,User2,UserN user
    class OpenWebUI web
    class RAGCore,EmbeddingService app
    class VectorDB,PostgresDB db
    class LocalLLM llm
    class VolumeKB,VolumeChat volume
```

### 4. Advanced RAG Retrieval Strategy

```mermaid
graph TD
    A[User Query] --> B{Query Analysis}
    B --> B1[Query Rewriting/Expansion]
    B1 --> B2{Additional Data Required?}

    B2 -- "Yes" --> C[Formulate Search Queries]
    B2 -- "No" --> H

    C --> D[Retrieve Initial Context]
    D --> E{Retrieve Data from Vector DB};
    E --> F[Re-rank Results];
    F --> G[Augment Prompt with Context];
    G --> H{Generate Response with LLM}; 

    H --> I{Evaluate Response};
    I -- "Good" --> J[Return Response to User];
    I -- "Needs Refinement" --> B;

    subgraph "Query Preprocessing"
        direction LR
        B
        B1
        B2
        C
    end

    subgraph "Retrieval & Re-ranking"
        direction LR
        D
        E
        F
    end

    subgraph "Generation & Iterative Refinement"
        direction LR
        G
        H
        I
    end

    classDef queryPreprocessing fill:#lightblue,stroke:#333,stroke-width:2px;
    classDef retrievalReranking fill:#lightgreen,stroke:#333,stroke-width:2px;
    classDef generationRefinement fill:#lightcoral,stroke:#333,stroke-width:2px;

    class B,B1,B2,C queryPreprocessing;
    class D,E,F retrievalReranking;
    class G,H,I generationRefinement;
    class A,J fill:#eee,stroke:#333,stroke-width:2px;
```

### 5. Phase 1 Prototype: Minimal Viable RAG Flow

```mermaid
graph TD
    subgraph "Minimal Viable MCP Client (e.g., Python Script)"
        direction LR
        UserInput[User Enters Query via Script/Simple UI] --> ClientApp{Client Application};
        ClientApp -- "Sends HTTP Request (Query)" --> MCPServerEndpoint;
        MCPServerEndpoint -- "Receives HTTP Response (LLM Output)" --> ClientApp;
        ClientApp --> DisplayResponse[Displays LLM Response];
    end

    subgraph "Minimal Viable RAG Core (MCP Server)"
        direction TB
        MCPServerEndpoint[MCP Server Endpoint e.g., FastAPI];
        
        subgraph "Simplified RAG Pipeline"
            direction TB
            QueryInput[Raw User Query] --> VectorDBQuery;
            VectorDBQuery{Basic Retrieval from Vector DB} --> RetrievedChunks;
            RetrievedChunks --> PromptAugmentation{Basic Prompt Augmentation};
            PromptAugmentation -- "Augmented Prompt (Query + Chunks)" --> LLMInterface;
            LLMInterface{LLM Call } --> LLMOutput[Generated Text];
        end

        PreloadedVectorDB[("Pre-loaded In-Memory Vector DB <br/> (e.g., FAISS/ChromaDB with <br/> 5-10 manually embedded chunks)")] -.- VectorDBQuery;
        MCPServerEndpoint --> QueryInput;
        LLMOutput --> MCPServerEndpoint;
    end

    classDef clientSide fill:#cde,stroke:#333,stroke-width:2px;
    classDef serverSide fill:#fde,stroke:#333,stroke-width:2px;
    classDef processStep fill:#e6ffe6,stroke:#333,stroke-width:1px;
    classDef dataStore fill:#ffe6cc,stroke:#333,stroke-width:1px;

    class UserInput,ClientApp,DisplayResponse clientSide;
    class MCPServerEndpoint,QueryInput,VectorDBQuery,RetrievedChunks,PromptAugmentation,LLMInterface,LLMOutput serverSide;
    class PreloadedVectorDB dataStore;
    class VectorDBQuery,PromptAugmentation,LLMInterface processStep;
```
