from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "CMDB Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database configuration
    database_type: str = "memory"  # Options: "mongodb", "memory"
    #DONT CHECK THIS IN!!
    mongodb_url: str = ""
    database_name: str = "cmdb_shm"

    openai_api_key: str = ""

    enable_ai_field_mapping: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()