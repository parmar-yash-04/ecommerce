from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    smtp_from: str
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

settings = Settings()