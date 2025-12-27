from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # ModelScope
    modelscope_api_key: str = ""
    qwen_model: str = "qwen-turbo"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./data/uploads"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
