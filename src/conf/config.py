from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis: str
    redis_host: str
    redis_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int
    postgres_host: str
    # email_sender: EmailStr
    # sendgrid_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
