""" Management Scripts """

import os

from flask.ext.script import Manager

from grocery_list import app

from grocery_list.database import Base, engine
from tests import test_data

manager = Manager(app)

@manager.command
def run():
    """Run development server"""
    # Retrieve port from environment if available
    port = int(os.environ.get("PORT", 8000))
    app.run(host="127.0.0.1", port=port)

@manager.command
def resetdb():
    """ Drop and create development database """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    table_count = len([x for x in engine.table_names()])
    print("Database reset. {} tables added.".format(table_count))

@manager.command
def seed_data():
    """ Add all test data to development database """
    resetdb()
    test_data.add_all()
    print("Seed data added.")



if __name__ == "__main__":
    manager.run()