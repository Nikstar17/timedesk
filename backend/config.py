import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/refresh"


class DevConfig(BaseConfig):
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    DEBUG = True


class ProdConfig(BaseConfig):
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    DEBUG = False
