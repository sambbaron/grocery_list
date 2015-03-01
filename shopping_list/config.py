""" Configuration Settings """

import os


class ProductionConfig(object):
    """Heroku Configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = False
    SECRET_KEY = os.environ.get("MY_SECRET_KEY")


class DevelopmentConfig(object):
    """Development Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgresql://sambbaron:1234@localhost:5432/shopping_list"
    DEBUG = True
    try:
        SECRET_KEY = os.environ["MY_SECRET_KEY"]
    except KeyError as e:
        print("{}: Secret key not set as environment variable. Setting as random.".format(e))
        SECRET_KEY = os.urandom(32)


class TestingConfig(object):
    """Development Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgresql://sambbaron:1234@localhost:5432/shopping_list_test"
    DEBUG = True
    SECRET_KEY = ""
