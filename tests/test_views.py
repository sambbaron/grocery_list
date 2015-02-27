""" Views Integration Tests """

import os
import unittest
import datetime

from werkzeug.security import generate_password_hash

from shopping_list import app
from shopping_list.models import *
from shopping_list.database import Base, engine, session

# App configuration for testing environment
os.environ["CONFIG_PATH"] = "shopping_list.config.TestingConfig"

class TestViews(unittest.TestCase):
    """ Views Integration Tests

    Methods:
        TestIndex - index view

    """

    def setUp(self):
        # Test client
        self.client = app.test_client()
        # Create tables in testing database
        Base.metadata.create_all(engine)

    def tearDown(self):
        session.close()
        # Remove tables from testing database
        Base.metadata.drop_all(engine)

    def simulate_login(self):
        """ Simulate user login within testing session """
        with self.client.session_transaction as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True



if __name__ == "__main__":
    unittest.main()