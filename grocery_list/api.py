""" All API Calls """

import json

from flask import request, Response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
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


@app.route("/api/user/<int:id>/profile", methods=["GET"])
@decorators.accept("application/json")
def user_profile_get(id):
    """ Retrieve user profile

    Return: user profile data
    """

    user = get_object(User, id)

    if type(user) == Response:
        return user

    data = json.dumps(user.as_dict_base(["password"]))
    return Response(data, 200, mimetype="application/json")

@app.route("/api/user/profile", methods=["POST"])
@decorators.accept("application/json")
def user_profile_post():
    """ Create new user

    Return: user profile data
    """
    data = request.json

    user = User()
    user.name = data["name"]
    user.email = data["email"]
    user.password = generate_password_hash(data["password"])

    session.add(user)
    session.commit()

    headers = {"Location": url_for("user_profile_get", id=user.id)}
    message = "Successfully created user profile"

    data_dict = user.as_dict_base(["password"])
    data_dict.update({"message":message})
    data_json = json.dumps(data_dict)

    return Response(data_json, 201, headers=headers,
                    mimetype="application/json")

@app.route("/api/user/<int:id>/profile", methods=["PUT"])
@decorators.accept("application/json")
def user_profile_put(id):
    """ Update user profile

    Return: user profile data
    """
    data = request.json

    user = get_object(User, id)

    # Test whether user exists
    if type(user) == Response:
        return user

    # Test current password match
    if not check_password_hash(user.password, data["password-current"]):
        message = "Current password is incorrect"
        data = json.dumps({"message": message})
        return Response(data, 401, mimetype="application/json")

    # Test whether new password is provided
    if data["password-new"] and data["password-new2"]:
        # Test whether new password entry matches
        if data["password-new"] == data["password-new2"]:
            # Update password
            user.password = generate_password_hash(data["password-new"])
        else:
            message = "New passwords do not match - update terminated"
            data = json.dumps({"message": message})
            return Response(data, 400, mimetype="application/json")

    # Update other user attributes
    user.name = data["name"]
    user.email = data["email"]

    session.commit()

    headers = {"Location": url_for("user_profile_get", id=user.id)}
    message = "Successfully updated user profile"

    data_dict = user.as_dict_base(["password"])
    data_dict.update({"message":message})
    data_json = json.dumps(data_dict)

    return Response(data_json, 200, headers=headers,
                    mimetype="application/json")

@app.route("/api/user/<int:user_id>/store/<int:store_id>", methods=["PUT"])
@decorators.accept("application/json")
def user_store_put(user_id, store_id):
    """ Update my store (UserStore)

    Return: user store data
    """
    data = request.json

    # Lookup UserStore record
    user_store = session.query(UserStore).filter(UserStore.user_id == user_id,
                                                 UserStore.store_id == store_id).first()
    if user_store is None:
        message = "Could not find store with id {}".format(store_id)
        user_store = json.dumps({"message": message})
        return Response(user_store, 404, mimetype="application/json")

    # Update user_store attributes
    # for key, value in data.items():
    #     print("Test user_store.key = {}".format(user_store.getattr(key)))
    #     user_store.key = value

    user_store.store.name = data["store.name"]

    session.commit()

    headers = {"Location": url_for("user_profile_get", id=user_store.user_id)}
    message = "Successfully updated user store"

    data_dict = user_store.as_dict_model()
    data_dict.update({"message":message})
    data_json = json.dumps(data_dict)

    return Response(data_json, 200, headers=headers,
                    mimetype="application/json")