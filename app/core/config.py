from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Integração externa de cotações (usada em POST /v1/exchanges/sync)
    EXCHANGE_API_BASE_URL: str = "https://economia.awesomeapi.com.br"
    EXCHANGE_API_PAIRS: str = "USD-BRL,EUR-BRL"
    EXCHANGE_API_TIMEOUT: int = 10

    model_config = {"env_file": ".env"}


settings = Settings()
