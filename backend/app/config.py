from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    laws_api_url: str = "http://api:8080"

    news_api_key: str = ""
    news_api_url: str = "https://newsapi.org/v2/everything"

    wikipedia_api_url: str = "https://en.wikipedia.org/w/api.php"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()