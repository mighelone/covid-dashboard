"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# from myapi.commons.apispec import APISpecExt


db = SQLAlchemy()
ma = Marshmallow()
