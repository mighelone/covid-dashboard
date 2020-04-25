import os


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///covid.db"


class LocalConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://covid:FabrizioCorona@localhost:5432/covid"
    )
    DEBUG = True
    TESTING = True


class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", None)
