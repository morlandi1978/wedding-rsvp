from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "wedding_rsvp"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    SECRET_KEY: str = "changeme"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme123"
    FRONTEND_URL: str = "http://localhost:8080"
    COUPLE_NAME: str = "Gli Sposi"
    WEDDING_DATE: str = ""
    WEDDING_LOCATION: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
