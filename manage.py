""" Management Scripts """

import os
import json

from flask.ext.script import Manager

from shopping_list import app

from shopping_list.database import Base, engine
from shopping_list import models
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

@manager.command
def preload_data():
    """ Add all preloaded default data to production database

        Retrieve from preload_data.json file
        Schema: {Model Name: [Values Dictionary]}
    """
    resetdb()

    root_path = os.path.dirname(os.path.realpath(__file__))
    with open(root_path + "/shopping_list/preload_data.json") as data_file:
        data = json.load(data_file)

    for model_name, values_list in sorted(data.items()):
        table = getattr(getattr(models, model_name),"__table__")
        ins = getattr(table, "insert")().values(values_list)
        engine.execute(ins)
        print("{} data added.".format(model_name))

if __name__ == "__main__":
    manager.run()