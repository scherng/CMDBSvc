from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "CMDB Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    database_url: str = "sqlite:///./cmdb.db"
    
    
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    extraction_model: str = "gpt-3.5-turbo"
    extraction_temperature: float = 0.1
    extraction_max_tokens: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()