from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Integração externa de cotações (usada em POST /v1/exchanges/sync)
    EXCHANGE_API_BASE_URL: str = "https://economia.awesomeapi.com.br"
    EXCHANGE_API_TOKEN: str = ""
    EXCHANGE_API_TIMEOUT: int = 15

    # Integração com Airtable
    AIRTABLE_BASE_URL: str = ""
    AIRTABLE_TOKEN: str = ""
    AIRTABLE_TABLE_CURRENCY: str = "Currency"
    AIRTABLE_TABLE_EXCHANGE: str = "Exchange"
    AIRTABLE_TIMEOUT: int = 30

    model_config = {"env_file": ".env"}


settings = Settings()
