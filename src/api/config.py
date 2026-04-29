import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/nourisher")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "ml/models/finetuned-llama")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "1536"))
    LOAD_IN_4BIT: bool = os.getenv("LOAD_IN_4BIT", "true").lower() in ("1", "true", "yes")


settings = Settings()
