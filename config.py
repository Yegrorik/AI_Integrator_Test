from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    telegram_bot_token: str
    groq_api_key: str

    # Можно вынести в .env при необходимости
    groq_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
