import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

# Load .env from project root (one level above backend/)
from dotenv import load_dotenv
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env", override=False)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "BrandSentinel AI"
    version: str = "1.0.0"
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'brandsentinel.db'}")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_backup_keys: str = os.getenv("GEMINI_BACKUP_KEYS", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    custom_llm_endpoint: str = os.getenv("CUSTOM_LLM_ENDPOINT", "https://integrate.api.nvidia.com/v1")
    custom_llm_api_key: str = os.getenv("CUSTOM_LLM_API_KEY", "") or os.getenv("NVIDIA_API_KEY", "")
    # Cloud / Local LLM (NVIDIA NIM / Ollama / LM Studio / any OpenAI-compatible endpoint)
    local_llm_endpoint: str = os.getenv("LOCAL_LLM_ENDPOINT", "https://integrate.api.nvidia.com/v1")
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "nvidia/nemotron-3.5-super-vl-120b-a12b")
    local_llm_enabled: bool = os.getenv("LOCAL_LLM_ENABLED", "true").lower() in ("true", "1", "yes")
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "*"
    ]
    upload_dir: Path = UPLOAD_DIR

settings = Settings()

def get_settings() -> Settings:
    return settings

def update_gemini_key(new_key: str):
    settings.gemini_api_key = new_key.strip()
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

