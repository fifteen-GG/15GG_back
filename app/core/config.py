import secrets
import os

from pydantic import BaseSettings
from dotenv import dotenv_values

env = dotenv_values('.env')


DB_URI = 'postgresql://' + \
    f'{os.environ.get("DB_USERNAME")}:{os.environ.get("DB_PASSWORD")}' + \
    f'@{os.environ.get("DB_HOST")}:{os.environ.get("DB_PORT")}/{os.environ.get("DB_NAME")}'


class Settings(BaseSettings):
    API_ROOT: str = '/api/v1'
    PROJECT_NAME: str = 'app_15gg'
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI: str = DB_URI

    class Config:
        env_file = '.env'


settings = Settings()
