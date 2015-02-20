""" All API Calls """

import json

from flask import request, Response
from jsonschema import validate, ValidationError

from . import app
from . import decorators
from .database import session
from .models import *


def get_object(model, id):
    """ Retrieve all data for a single object

    Returns:
        One record or response with 404 error
    """
    data = session.query(model).get(id)

    if data:
        return data
    else:
        message = "Could not find song with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")


def validate_schema(data, schema):
    """ Validate JSON against schema

    Returns:
        Response if error
    """
    try:
        validate(data, schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

