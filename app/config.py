from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    POSTGRES_HOST: str = Field(env="POSTGRES_HOST", default="db")
    POSTGRES_PORT: int = Field(env="POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = Field(env="POSTGRES_DB", default="secrets")
    POSTGRES_USER: str = Field(env="POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD", default="postgres")
    ENCRYPTION_KEY: str = Field(env="ENCRYPTION_KEY")
    MIN_TTL: int = Field(env="MIN_TTL", default=300)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
