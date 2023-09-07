from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from sys import stdout
from loguru import logger


class BotSettings(BaseSettings):
    token: SecretStr
    admin_id: Optional[int] = None


class LogSettings(BaseSettings):
    level: Optional[str] = 'INFO'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter='__')
    bot: BotSettings
    log: LogSettings = LogSettings()


settings = Settings()

logger.remove()
logger.add(stdout, level=settings.log.level)
logger.debug(settings.model_dump_json(indent=2))
