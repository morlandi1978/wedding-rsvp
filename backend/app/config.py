from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str = "changeme"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme123"
    FRONTEND_URL: str = "http://localhost"
    COUPLE_NAME: str = "Gli Sposi"
    WEDDING_DATE: str = ""
    WEDDING_LOCATION: str = ""

    class Config:
        env_file = ".env"


settings = Settings()