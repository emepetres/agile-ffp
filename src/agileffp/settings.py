from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="dev.env", env_file_encoding="utf-8")
    MICROSOFT_CLIENT_ID: str = "no_client_id_provided"
    MICROSOFT_CLIENT_SECRET: str = "no_client_secret_provided"


app_settings = AppSettings()
