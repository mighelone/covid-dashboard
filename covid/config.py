import os


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///covid.db"


class LocalConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:example@127.0.0.1:3306/covid"
    DEBUG = True
    TESTING = True


class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", None)
