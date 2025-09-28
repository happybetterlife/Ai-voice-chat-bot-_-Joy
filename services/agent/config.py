from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    LIVEKIT_URL: str
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str
    OPENAI_API_KEY: str
    DEEPGRAM_API_KEY: str
    ELEVENLABS_API_KEY: str
    DB_URL: str = 'sqlite:///./memory.db'
    RAG_BACKEND: str = 'faiss'
    PINECONE_API_KEY: str | None = None
    PINECONE_ENV: str | None = None
    PINECONE_INDEX: str | None = None
    AGENT_SYSTEM_PROMPT: str = 'You are a helpful, concise voice agent.'
    AGENT_VOICE_PROVIDER: str = 'elevenlabs'
    AGENT_VOICE_ID: str | None = None
    DEFAULT_VOICE_ID: str = 'Rachel'
    HISTORY_RELOAD_TURNS: int = 12
    class Config:
        env_file = '.env'
settings = Settings()
