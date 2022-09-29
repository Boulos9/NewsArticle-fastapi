from pydantic import BaseSettings, PostgresDsn, Field
from functools import lru_cache

class Settings(BaseSettings):
	secret_key: str
	algorithm: str
	token_expire: int = Field(...,env="ACCESS_TOKEN_EXPIRE_MINUTES")
	database_credentials: PostgresDsn
	database_test_credentials: PostgresDsn
	incorrect_secret_key: str

	class Config:
		env_file = '.env'


@lru_cache
def get_settings():
	return Settings()