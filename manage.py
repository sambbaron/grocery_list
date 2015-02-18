""" Management Scripts """

import os

from flask.ext.script import Manager

from grocery_list import app

from grocery_list.database import Base, engine
from grocery_list.models import *

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
    print("Tables Added:")
    for table in engine.table_names():
        print(table)

if __name__ == "__main__":
    manager.run()