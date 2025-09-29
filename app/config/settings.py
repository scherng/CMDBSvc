from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "CMDB Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database configuration
    database_type: str = "memory"  # Options: "mongodb", "memory"
    database_name: str = "cmdb_shm"

    #need to be populated to actually hit end point. Or just use False in enable_ai_field_mapping
    openai_api_key = ""
    mongodb_url = ""

    enable_ai_field_mapping: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()