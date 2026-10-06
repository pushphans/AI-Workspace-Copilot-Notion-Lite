from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    DATABASE_URL : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRY_IN_MINUTES : int
    REFRESH_TOKEN_EXPIRY_IN_DAYS : int
    JWT_SECRET_KEY : str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )



settings = Settings()