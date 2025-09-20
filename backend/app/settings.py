from pydantic import BaseModel
import os

class Settings(BaseModel):
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    host: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    port: int = int(os.getenv("SERVICE_PORT", "8080"))
    hf_offline: bool = os.getenv("HF_HUB_OFFLINE", "false").lower() == "true"
    transformers_cache: str | None = os.getenv("TRANSFORMERS_CACHE")

settings = Settings()
