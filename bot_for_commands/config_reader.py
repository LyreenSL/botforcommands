from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    bot_token: SecretStr
    db_address: SecretStr
    test_db_address: SecretStr
    log_level: str


config = Settings()

