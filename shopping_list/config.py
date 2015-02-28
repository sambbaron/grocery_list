""" Configuration Settings """

import os


class HerokuConfig(object):
    """Heroku Configuration"""
    SQLALCHEMY_DATABASE_URI = "postgres://whjpwdpzmdwrhc:4ebb7mC0iWfPVHW5FYBjKGH9uk@ec2-23-23-180-133.compute-1.amazonaws.com:5432/d3p4q8u138oe1m"
    DEBUG = False
    SECRET_KEY = os.urandom(32)


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
