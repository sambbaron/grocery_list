""" Configuration Settings """

import os

class DevelopmentConfig(object):
    """Development Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgresql://sambbaron:1234@localhost:5432/grocery_list"
    DEBUG = True
    SECRET_KEY = os.environ.get("GROCERYLIST_SECRET_KEY", os.urandom(32))
    # SECRET_KEY = os.environ.get("GROCERYLIST_SECRET_KEY", "")

class TestingConfig(object):
    """Development Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgresql://sambbaron:1234@localhost:5432/grocery_list_test"
    DEBUG = True
    SECRET_KEY = ""
