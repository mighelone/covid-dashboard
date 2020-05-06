"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# from myapi.commons.apispec import APISpecExt


db = SQLAlchemy()
ma = Marshmallow()
