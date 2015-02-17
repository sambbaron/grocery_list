""" Management Scripts """

import os

from flask.ext.script import Manager

from grocery_list import app

manager = Manager(app)

@manager.command
def run():
    """Run development server"""
    # Retrieve port from environment if available
    port = int(os.environ.get("PORT", 8000))
    app.run(host="127.0.0.1", port=port)


if __name__ == "__main__":
    manager.run()