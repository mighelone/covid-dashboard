import os


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = "sqlite:///covid.db"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.0/"
    # OPENAPI_REDOC_PATH = "/redoc"
    # OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"


class LocalConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:example@127.0.0.1:3306/covid"
    DEBUG = True
    TESTING = True


class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", None)
