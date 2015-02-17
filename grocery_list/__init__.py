""" Application Initialization and Setup """

import os
from flask import Flask

# Create app
app = Flask(__name__)

# Read configuration file
config_path = os.environ.get("CONFIG_PATH", "grocery_list.config.DevelopmentConfig")
app.config.from_object(config_path)

# Import views
from . import views

# Database initialization
from .database import Base, engine
Base.metadata.create_all(engine)