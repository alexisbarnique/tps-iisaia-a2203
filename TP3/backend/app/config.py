from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    test_database_url: str = ""
    secret_key: str

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_not_be_placeholder(cls, v: str) -> str:
        if v == "change-this-to-a-random-secret-key":
            raise ValueError("SECRET_KEY must be changed from the default placeholder")
        return v

    class Config:
        env_file = ".env"


settings = Settings()
