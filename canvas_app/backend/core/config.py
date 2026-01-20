"""Application configuration."""
from pathlib import Path
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback if pydantic-settings not installed
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "NormCode Canvas"
    debug: bool = True
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # API Keys
    dashscope_api_key: str | None = None
    
    # Paths - use centralized path utilities for frozen/dev mode compatibility
    @property
    def project_root(self) -> Path:
        try:
            from core.path_utils import get_app_dir
            return get_app_dir()
        except ImportError:
            return Path(__file__).parent.parent.parent.parent
    
    @property
    def infra_path(self) -> Path:
        try:
            from core.path_utils import get_infra_dir
            return get_infra_dir()
        except ImportError:
            return self.project_root / "infra"
    
    # Default LLM settings
    default_llm_model: str = "demo"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment


settings = Settings()
