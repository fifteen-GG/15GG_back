import secrets
import os

from pydantic import BaseSettings
from dotenv import dotenv_values

if dotenv_values('.env'):
    env = dotenv_values('.env')
    env['DB_HOST'] = '127.0.0.1'
else:
    env = os.environ


DB_URI = 'postgresql://' + \
    f'{env.get("DB_USERNAME")}:{env.get("DB_PASSWORD")}' + \
    f'@{env.get("DB_HOST")}:{env.get("DB_PORT")}/{env.get("DB_NAME")}'


class Settings(BaseSettings):
    API_ROOT: str = '/api/v1'
    PROJECT_NAME: str = 'app_15gg'
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI: str = DB_URI
    AMQP_HOST: str = env.get('AMQP_HOST')

    class Config:
        env_file = '.env'


settings = Settings()
