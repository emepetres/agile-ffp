from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="dev.env", env_file_encoding="utf-8")
    MY_SAMPLE_VARIABLE: str = "DEFAULT_VALUE"
    OTHER_VARIABLE: int = 1


app_settings = AppSettings()
