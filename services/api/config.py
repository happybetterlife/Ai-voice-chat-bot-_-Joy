from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    LIVEKIT_URL: str = os.getenv('LIVEKIT_URL', '')
    LIVEKIT_API_KEY: str = os.getenv('LIVEKIT_API_KEY', '')
    LIVEKIT_API_SECRET: str = os.getenv('LIVEKIT_API_SECRET', '')
    DB_URL: str = os.getenv('DB_URL', 'sqlite:///./memory.db')

    class Config:
        env_file = '.env'

settings = Settings()

# Debug: Print settings at startup
print(f"LIVEKIT_URL: {settings.LIVEKIT_URL}")
print(f"LIVEKIT_API_KEY: {settings.LIVEKIT_API_KEY[:10]}..." if settings.LIVEKIT_API_KEY else "LIVEKIT_API_KEY: (empty)")
