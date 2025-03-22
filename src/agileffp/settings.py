from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="dev.env", env_file_encoding="utf-8")
    DEBUG: bool = False
    RELOAD: bool = False


app_settings = AppSettings()
