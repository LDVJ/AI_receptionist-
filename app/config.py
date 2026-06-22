from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER : str
    DB_PASSWORD  : str
    DB_HOST : str
    DB_PORT : int
    DB_NAME : str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore" # it means if someo defined variable don't match with any data in .env ignore it don't throw error
        # extra = "forbid" it will throw error as it is alternative of ignore
    )


settings = Settings()
