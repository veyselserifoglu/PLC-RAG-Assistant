from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

class LLMSettings(BaseSettings):
    model_identifier: str = "default_local_llm_model"
    temperature: float = 0.7
    max_tokens: int = 1024

class VectorStoreSettings(BaseSettings):
    vector_store_type: Literal["ChromaDB"] = "ChromaDB"
    collection_name: str = "default_plc_collection"
    retrieval_k: int = 5
    vector_database_uri: Optional[str] = None 

class DatabaseSettings(BaseSettings):
    database_type: Literal["sqlite", "postgresql"] = "postgresql"
    sql_database_uri: Optional[str] = None

class AppSettings(BaseSettings):
    llm: LLMSettings = LLMSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    database: DatabaseSettings = DatabaseSettings()
    logging_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_nested_delimiter='__', # e.g., LLM__MODEL_IDENTIFIER for env vars
        extra='ignore'
    )

# Global settings instance.
settings = AppSettings()

# Example usage (optional, for testing here)
if __name__ == "__main__":
    print("\nLoaded Application Settings:")
    print(f"  LLM Model: {settings.llm.model_identifier}")
    print(f"  LLM Temperature: {settings.llm.temperature}")
    print(f"  Vector Store Type: {settings.vector_store.vector_store_type}")
    print(f"  Vector Store Path: {settings.vector_store.vector_database_uri}")
    print(f"  Vector Store Collection: {settings.vector_store.collection_name}")
    print(f"  Database Type: {settings.database.database_type}")
    print(f"  SQLite Path: {settings.database.sql_database_uri}")
    print(f"  Logging Level: {settings.logging_level}")
