from functools import lru_cache

from pydantic_settings import BaseSettings


class CoreSettings(BaseSettings):
    APP_NAME: str = "HoroShop"
    DEBUG: bool = False


class PostgresSettings(BaseSettings):
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PGPORT: int = 5432

    @property
    def DATABASE_ASYNC_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@"
            f"{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"
        )


class Settings(CoreSettings, PostgresSettings):
    pass


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
