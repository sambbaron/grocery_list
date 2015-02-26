""" Application Views """

from flask import render_template, redirect, url_for, request, abort
from flask.ext.login import current_user, login_user, logout_user, flash, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import update, select

from . import app
from .database import session
from .models import *
from .utils import update_from_form

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
        return redirect(url_for("store_get"))


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
            flash("Logged in successfully.", "success")
            return redirect(request.args.get("next") or url_for("index"))
        else:
            # Unsuccessful login
            flash("Incorrect username or password", "danger")
            return redirect(url_for("login"))

    # GET request
    if current_user.is_anonymous() == True:
        return render_template("login.html")
    else:
        return redirect(url_for("index"))


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


@app.route("/stores/new", methods=["GET"])
@app.route("/stores/<int:id>", methods=["GET"])
@app.route("/stores", methods=["GET"])
@login_required
def store_get(id=None):
    """ Retrieve all stores list and single store detail form

    Return:
        New Store: Empty store detail form
        Single Store: Store detail form for single store
        All Stores: All store list with empty store detail form
    """
    # Retrieve all stores for current user
    stores = session.query(UserStore).filter(UserStore.user_id == current_user.get_id()).all()

    # If no Store, select first store associated with current user
    if not id:
        id = session.query(UserStore.store_id).filter(UserStore.user_id == current_user.get_id()).first()


    # Single store provided
    if id is not None:
        # Retrieve single selected store
        user_store = session.query(UserStore).filter(UserStore.user_id == int(current_user.get_id()),
                                                     UserStore.store_id == id).first()
        # Test whether store exists
        if user_store is None:
            flash("Could not find store with id {}".format(UserStore.store_id),"danger")
            return redirect(url_for("store_get"))
    # New store requested
    elif request.path == "/stores/new":
        # Set as new store entry
        user_store = "new"
    else:
        # Set as no store entry
        user_store = "empty"

    return render_template("stores.html", stores=stores, store=user_store)


@app.route("/stores/new", methods=["POST"])
@login_required
def store_post():
    """ Create new store

    Add store record and associate with current user

    Return:
        Store page
    """
    data = request.form

    # Create new Store
    store = Store(name="New Store")
    session.add(store)
    session.commit()

    # Associate new Store with current User
    user_store = UserStore(store_id = store.id,
                           user_id = current_user.get_id()
    )
    session.add(user_store)
    session.commit()

    # Update data in new record
    if not update_from_form(data, Store=store.id, UserStore=(user_store.user_id, user_store.store_id)):
        flash("Server error in creating store", "danger")
        return redirect(request.url)

    flash("Successfully created store", "success")
    return redirect(request.url)

@app.route("/stores/<int:id>", methods=["PUT", "POST"])
@login_required
def store_put(id):
    """ Edit existing store

    Return:
        Single store page
    """
    # Return form data
    data = request.form
    # Set UserStore record
    user_store = session.query(UserStore).filter(UserStore.user_id == int(current_user.get_id()),
                                                     UserStore.store_id == id).first()
    # Test whether UserStore record exists
    if not user_store:
        flash("Could not find store with id {} for current user".format(UserStore.store_id),"danger")
        return redirect(url_for("store_get"))

    # Update data
    if not update_from_form(data):
        flash("Server error in updating store", "danger")
        return redirect(request.url)

    flash("Successfully updated store", "success")
    return redirect(request.url)

# TODO: Default value not passing through form


@app.route("/routes", methods=["GET"])
@app.route("/stores/<int:store_id>/routes/new", methods=["GET"])
@app.route("/stores/<int:store_id>/routes/<int:route_id>", methods=["GET"])
@app.route("/stores/<int:store_id>/routes", methods=["GET"])
@login_required
def route_get(store_id=None, route_id=None):
    """ Retrieve all routes list and single route detail form

    Retrieve all stores associated with route

    Return:
        New route: Empty route detail form
        Single route: route detail form for single route
        All routes: All route list with empty route detail form
    """
    # Retrieve all Stores for current User
    stores = session.query(UserStore).filter(UserStore.user_id == current_user.get_id()).all()

    # If no Stores, then redirect to Stores page
    if not stores:
        flash("You do not have any stores setup. Please setup a store first.", "warning")
        return redirect(url_for("store_get"))

    # If no selected Store or Route, set to first Store for user
    if not store_id and not route_id:
        store_id = session.query(UserStore.user_id).filter(UserStore.user_id == current_user.get_id()).first()

    # If Route provided, but no Store, lookup Store associated with Route
    if route_id and not store_id:
        store = session.query(Store).filter(Store.route.contains(session.query(Route).get(route_id))).first()
    else:
        # Set Store object using provided id
        store = session.query(Store).get(store_id)

    # If Store provided, but no Route, lookup first Route associated with Store
    if store_id and not route_id:
        route = session.query(Route).filter(Route.store.contains(store)).first()
    else:
        # Set Route object using provided id
        route = session.query(Route).get(route_id)

    # Retrieve all routes for current User and selected Store
    routes = session.query(Route).filter(Route.user_id == current_user.get_id(), Route.store.contains(store)).all()

    # Create Route Groups dictionary
    route_groups = {}

    # Single Route provided
    if route is not None:
        # Retrieve related Item Groups ordered by Route Order
        route_groups = session.query(RouteGroup).filter(RouteGroup.route_id == route.id).order_by(RouteGroup.route_order)

        # Test whether Route exists
        if route is None:
            flash("Could not find route with id {}".format(route.route_id),"danger")
            return redirect(url_for("route_get"))
    # New Route requested
    elif request.path.find("/routes/new") > -1:
        # Set as new Route entry
        route = "new"
    else:
        # Set as no Route entry
        route = "empty"

    # Create Item Groups list for selection
    item_groups = session.query(ItemGroup).all()

    return render_template("routes.html", stores=stores, store=store,
                           routes=routes, route=route,
                           route_groups=route_groups, item_groups=item_groups
    )


@app.route("/stores/<int:store_id>/routes/new", methods=["POST"])
@login_required
def route_post(store_id):
    """ Create new Route

    Associate new Route with Store

    Return:
        Route put method to update data to new record
    """
    data = request.form

    # Set Store object
    store = session.query(Store).get(store_id)

    # Create new Route
    route = Route(name="New Route",
                  user_id=current_user.get_id(),
                  store=[store]
    )

    session.add(route)
    session.commit()

    # Update data in new record
    if not update_from_form(data, Route=route.id):
        flash("Server error in creating route", "danger")
        return redirect(request.url)

    flash("Successfully created route", "success")
    return redirect(request.url)


@app.route("/stores/<int:store_id>/routes/<int:route_id>", methods=["PUT", "POST"])
@login_required
def route_put(store_id, route_id):
    """ Edit existing Route

    Return:
        Single Route page
    """
    # Return form data
    data = request.form
    # Set Route record
    route = session.query(Route).get(route_id)

    # Test whether Route record exists
    if not route:
        flash("Could not find route with id {}".format(route_id),"danger")
        return redirect(url_for("route_get"))

    # Update data
    if not update_from_form(data):
        flash("Server error in updating route", "danger")
        return redirect(request.url)

    flash("Successfully updated route", "success")
    return redirect(request.url)


@app.route("/lists")
@login_required
def lists():
    return render_template("lists.html")
