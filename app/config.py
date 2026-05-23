from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    jwt_secret: str = "change-me"
    apple_bundle_id: str = "com.yourcompany.artfolio"
    database_url: str = "postgresql+asyncpg://artfolio:artfolio@localhost:5432/artfolio"
    daily_augment_limit: int = 10
    daily_translate_limit: int = 10

    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1500
    openai_timeout: int = 30

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
