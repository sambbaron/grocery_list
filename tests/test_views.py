""" Views Integration Tests """

import os
import unittest

from werkzeug.security import generate_password_hash

from grocery_list import app
from grocery_list import models
from grocery_list.database import Base, engine, session

# App configuration for testing environment
os.environ["CONFIG_PATH"] = "grocery_list.config.TestingConfig"

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
        # Create example user
        self.user = models.User(name="Testy",
                                email="testy@test.com",
                                password=generate_password_hash("test")
        )
        session.add(self.user)
        session.commit()

    def tearDown(self):
        session.close()
        # Remove tables from testing database
        Base.metadata.drop_all(engine)



if __name__ == "__main__":
    unittest.main()