import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    NVIDIA_API_KEY=os.getenv("API_KEY")
    MODEL_NAME=os.getenv("MODEL")
    BASE_URL = os.getenv("BASE_URL")

    MONGODB_URI = os.getenv("MONGODB_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    CHECKPOINT_COLLECTION = os.getenv("CHECKPOINT_COLLECTION")
    CHECKPOINT_WRITES_COLLECTION=os.getenv("CHECKPOINT_WRITES_COLLECTION")

    GEO_URL=os.getenv("GEO_URL")
    WEATHER_URL=os.getenv("WEATHER_URL")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

settings = Settings()
