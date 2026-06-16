import os
from pydantic_settings import BaseSettings, SettingsConfigDict


# Decide which env file to load
ENV = os.getenv("ENV", "dev")

if ENV == "production":
    env_file = ".env.prod"
elif ENV == "test":
    env_file = ".env.test"
else:
    env_file = ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        extra="ignore"
    )

    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    COHERE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    used: str = ""
    chatbot_vector_db_used: str = "local"
    chatbot_vector_db_local_host: str = "localhost"
    chatbot_vector_db_local_database: str = "ragdb"
    chatbot_vector_db_local_user: str = "postgres"
    chatbot_vector_db_local_password: str = ""
    chatbot_vector_db_local_port: int = 5432
    chatbot_vector_db_prod_url: str = ""
    env: str = ENV

settings = Settings()
