from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BACKEND_PORT: int = 8000
    MODEL_PATH: str = "model/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.80

    class Config:
        env_file = ".env"
        extra = "ignore" # Ignorar variables extra del .env (como CONTAINER_NAME)

def get_settings():
    return Settings()