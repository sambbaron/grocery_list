""" Application Views """

from flask import render_template, redirect, url_for, request, abort
from flask.ext.login import current_user, login_user, logout_user, flash, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import update, select

from . import app
from .database import session
from .models import *

@app.route("/")
def index():
    """ App entry routing
    Login or go to page with data
    """

    # If no user, redirect to login
    if current_user.is_anonymous() == True:
        return redirect(url_for("login"))

    user_id = int(current_user.get_id())

    # Redirect to Lists if exist
    if session.query(List.id).filter(List.user_id == user_id).first() is not None:
        return redirect(url_for("lists"))
    # Redirect to Routes if exist
    elif session.query(Route.id).filter(List.user_id == user_id).first() is not None:
        return redirect(url_for("routes"))
    # Else redirect to Stores
    else:
        return redirect(url_for("stores_get"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Returns: Login page """

    if request.method == "POST":
        #HTML form entry
        email = request.form["email"]
        password = request.form["password"]
        # Return user
        user = session.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Successful login
            login_user(user)
            flash("Logged in successfully.")
            return redirect(request.args.get("next") or url_for("index"))
        else:
            # Unsuccessful login
            flash("Incorrect username or password", "danger")
            return redirect(url_for("login"))

    # GET request
    return render_template("login.html")


@app.route("/logout")
def logout():
    """ Returns: Login page """
    logout_user()
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET"])
def profile_get():
    """ Retrieve User Profile

    Returns:
        Empty profile template (signup), or
        Current user profile page
    """

    # New User signup
    if current_user.is_anonymous() == True:
        return render_template("profile.html")

    # Return existing User profile data
    user = session.query(User).get(int(current_user.get_id()))
    return render_template("profile.html",
                           name=user.name,
                           email=user.email
    )


@app.route("/profile/signup", methods=["POST"])
def profile_post():
    """ Create new user

    Input user profile and login new user

    Return:
        Route to stores
    """
    data = request.form

    user = User()

    # Test whether email already exists

    # Test whether new password is provided
    if data["password-new"] and data["password-new2"]:
        # Test whether new password entry matches
        if data["password-new"] == data["password-new2"]:
            # Update password
            user.password = generate_password_hash(data["password-new"])
        else:
            flash("New passwords do not match", "danger")
            return redirect(url_for("profile_get"))

    # Update other user attributes
    user.name = data["name"]
    user.email = data["email"]

    session.add(user)
    session.commit()

    login_user(user)
    flash("Successfully created user profile", "success")
    return redirect(url_for("stores"))


@app.route("/profile/<int:id>", methods=["PUT", "POST"])
def profile_put(id):
    """ Edit existing user profile

    Return:
        Refresh profile page
    """
    data = request.form

    user = session.query(User).get(id)

    if not user:
        flash("Could not find user with id {}".format(id), "danger")
        return redirect(url_for("index"))

    # Test current password match
    if not check_password_hash(user.password, data["password-current"]):
        flash("Current password is incorrect", "danger")
        return redirect(url_for("profile_get"))

    # Test whether new password is provided
    if data["password-new"] and data["password-new2"]:
        # Test whether new password entry matches
        if data["password-new"] == data["password-new2"]:
            # Update password
            user.password = generate_password_hash(data["password-new"])
        else:
            flash("New passwords do not match", "danger")
            return redirect(url_for("profile_get"))

    # Update other user attributes
    user.name = data["name"]
    user.email = data["email"]

    session.commit()

    flash("Successfully updated user profile", "success")
    return redirect(url_for("profile_get"))


@app.route("/stores", methods=["GET"])
@app.route("/stores/<int:id>", methods=["GET"])
@login_required
def stores_get(id=0):
    """ Retrieve all stores or single store

    All stores for list, single store for detail

    Return:
        stores template
    """
    # Retrieve all stores for current user
    stores = session.query(UserStore).filter(UserStore.user_id == current_user.get_id()).all()

    if id != 0:
        # Retrieve single selected store
        user_store = session.query(UserStore).filter(UserStore.user_id == int(current_user.get_id()),
                                                     UserStore.store_id == id).first()
        # Test whether store exists
        if user_store is None:
            flash("Could not find store with id {}".format(UserStore.store_id),"danger")
            return redirect(url_for("stores_get"))
    else:
        user_store = False

    return render_template("stores.html", stores=stores, store=user_store)


@app.route("/stores/<int:id>", methods=["PUT", "POST"])
def store_put(id):
    """ Edit existing store

    Return:
        Refresh store page
    """
    # Return form data
    data = request.form
    # Set UserStore record
    user_store = session.query(UserStore).filter(UserStore.user_id == int(current_user.get_id()),
                                                     UserStore.store_id == id).first()
    # Test whether UserStore record exists
    if not user_store:
        flash("Could not find store with id {}".format(UserStore.store_id),"danger")
        return redirect(url_for("stores_get"))

    # Set table objects for SQL update
    user_store_tbl = UserStore.__table__
    store_tbl = Store.__table__

    # Create dictionaries with data for UserStore and Store
    user_store_dict = {}
    store_dict = {}
    for key,value in data.items():
        key_part = key.partition(".")
        if key_part[0] == "store":
            store_dict.update({key_part[2]:value})
        else:
            user_store_dict.update({key_part[0]:value})

    # Update UserStore table
    stmt = user_store_tbl.update().values(user_store_dict).where(user_store_tbl.c.store_id == store_tbl.c.id)\
        .where(user_store_tbl.c.user_id == int(current_user.get_id())).where(user_store_tbl.c.store_id == id)
    engine.execute(stmt)

    # Update Store table
    stmt = store_tbl.update().values(store_dict).where(user_store_tbl.c.store_id == store_tbl.c.id)\
        .where(user_store_tbl.c.user_id == int(current_user.get_id())).where(user_store_tbl.c.store_id == id)
    engine.execute(stmt)

    flash("Successfully updated store", "success")
    return redirect("{}/{}".format(url_for("stores_get"), id))


@app.route("/routes")
@login_required
def routes():
    return render_template("routes.html")


@app.route("/lists")
@login_required
def lists():
    return render_template("lists.html")
