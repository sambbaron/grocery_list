""" Application Views """

from flask import render_template, redirect, url_for, request
from flask.ext.login import current_user, login_user, logout_user, flash, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import desc

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
    if current_user.is_anonymous():
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
        # HTML form entry
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
    if current_user.is_anonymous():
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
    if current_user.is_anonymous():
        return render_template("profile.html")

    # Return existing User profile data
    user = session.query(User).get(int(current_user.get_id()))
    return render_template("profile.html",
                           name=user.name,
                           email=user.email)


@app.route("/profile/signup", methods=["POST"])
def profile_add():
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


@app.route("/profile/<user_id>", methods=["PUT", "POST"])
def profile_update(user_id):
    """ Edit existing user profile

    Return:
        Refresh profile page
    """
    data = request.form

    user = session.query(User).get(user_id)

    if not user:
        flash("Could not find user with id {}".format(user_id), "danger")
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
@app.route("/stores/<store_id>", methods=["GET"])
@app.route("/stores", methods=["GET"])
@login_required
def store_get(store_id=None):
    """ Retrieve all stores list and single store detail form

    Return:
        New Store: Empty store detail form
        Single Store: Store detail form for single store
        All Stores: All store list with empty store detail form
    """
    # Set all Stores for current User
    stores = session.query(UserStore).filter(UserStore.user_id == current_user.get_id())\
        .order_by(UserStore.store_id).all()

    # Set selected Store
    # New Store requested
    if request.path.find("/stores/new") > -1:
        # Set as new Store entry
        store = "new"
    # If no Store, select first store associated with current user
    elif not store_id:
        store_id = session.query(UserStore.store_id).filter(UserStore.user_id == current_user.get_id())\
            .order_by(UserStore.store_id).first()
        store = session.query(Store).get(store_id)
    else:
        # Set Store object using provided id
        store = session.query(Store).get(store_id)

    return render_template("stores.html", view="store", stores=stores, store=store)


@app.route("/stores/new", methods=["POST"])
@login_required
def store_add():
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
    user_store = UserStore(store_id=store.id,
                           user_id=current_user.get_id())

    session.add(user_store)
    session.commit()

    # Create joined UserStore primary keys
    user_store_keys = [str(user_store.user_id), str(user_store.store_id)]
    user_store_keys = " ".join(user_store_keys)

    # Update data in new record
    if not update_from_form(data, Store=store.id, UserStore=user_store_keys):
        flash("Server error in creating store", "danger")
        return redirect(request.url)

    flash("Successfully created store", "success")
    return redirect(url_for("store_get", store_id=store.id))


@app.route("/stores/<store_id>", methods=["PUT", "POST"])
@login_required
def store_update(store_id):
    """ Edit existing store

    Return:
        Single store page
    """
    # Return form data
    data = request.form
    # Set UserStore record
    user_store = session.query(UserStore).filter(UserStore.user_id == int(current_user.get_id()),
                                                 UserStore.store_id == store_id).first()
    # Test whether UserStore record exists
    if not user_store:
        flash("Could not find store with id {} for current user".format(UserStore.store_id), "danger")
        return redirect(url_for("store_get"))

    # Update data
    if not update_from_form(data):
        flash("Server error in updating store", "danger")
        return redirect(request.url)

    flash("Successfully updated store", "success")
    return redirect(url_for("store_get", store_id=user_store.store_id))


@app.route("/stores/<store_id>/delete", methods=["POST", "DELETE"])
@login_required
def store_delete(store_id):
    """ Delete existing store

    Return:
        Stores page
    """

    # Set UserStore record
    user_store = session.query(UserStore).filter(UserStore.user_id == int(current_user.get_id()),
                                                 UserStore.store_id == store_id).first()
    # Test whether UserStore record exists
    if not user_store:
        flash("Could not find store with id {} for current user".format(UserStore.store_id), "danger")
        return redirect(url_for("store_get"))

    session.delete(user_store)
    session.commit()

    flash("Successfully deleted store", "success")
    return redirect(url_for("store_get"))


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
    # Set all Stores for current User
    stores = session.query(UserStore).filter(UserStore.user_id == current_user.get_id()) \
        .order_by(UserStore.store_id).all()

    # If no Stores, then redirect to Stores page
    if not stores:
        flash("You do not have any stores setup. Please setup a store first.", "warning")
        return redirect(url_for("store_get"))

    # Set selected Store
    # If no selected Store or Route, set to first Store for user
    if not store_id and not route_id:
        store_id = session.query(UserStore.store_id).filter(UserStore.user_id == current_user.get_id())\
            .order_by(UserStore.store_id).first()
        store = session.query(Store).get(store_id)
    # If Route provided, but no Store, lookup Store associated with Route
    elif route_id and not store_id:
        store = session.query(Store).filter(Store.route.contains(session.query(Route).get(route_id))).first()
    else:
        # Set Store object using provided id
        store = session.query(Store).get(store_id)

    # Set all Routes for current User and selected Store
    routes = session.query(Route).filter(Route.user_id == current_user.get_id(), Route.store.contains(store)) \
        .order_by(Route.id).all()

    # Set selected Route
    # New Route requested
    if request.path.find("/routes/new") > -1:
        # Set as new Route entry
        route = "new"
    # If Store provided, but no Route, lookup first Route associated with Store
    elif store_id and not route_id:
        route = session.query(Route).filter(Route.store.contains(store)).order_by(Route.id).first()
    else:
        # Set Route object using provided id
        route = session.query(Route).get(route_id)

    # Set Route Groups
    route_groups = {}
    if route and route != "new":
        # Retrieve related Item Groups ordered by Route Order
        route_groups = session.query(RouteGroup).filter(RouteGroup.route_id == route.id).order_by(RouteGroup.route_order)

    # Set Item Groups list for form input selection
    item_groups = session.query(ItemGroup).all()

    return render_template("routes.html", view="route",
                           stores=stores, store=store,
                           routes=routes, route=route,
                           route_groups=route_groups, item_groups=item_groups)


@app.route("/stores/<int:store_id>/routes/new", methods=["POST"])
@login_required
def route_add(store_id):
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
                  store=[store])

    session.add(route)
    session.commit()

    # Update data in new record
    if not update_from_form(data, Route=route.id):
        flash("Server error in creating route", "danger")
        return redirect(request.url)

    flash("Successfully created route", "success")
    return redirect(url_for("route_get",
                            store_id=store.id, route_id=route.id))


@app.route("/stores/<int:store_id>/routes/<int:route_id>", methods=["PUT", "POST"])
@login_required
def route_update(store_id, route_id):
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
        flash("Could not find route with id {}".format(route_id), "danger")
        return redirect(url_for("route_get"))

    # Update data
    if not update_from_form(data):
        flash("Server error in updating route", "danger")
        return redirect(request.url)

    # Renumber route order to remove duplicates
    route.renumber_route_order()

    flash("Successfully updated route", "success")
    return redirect(url_for("route_get",
                            store_id=route.store[0].id, route_id=route.id))


@app.route("/stores/<int:store_id>/routes/<int:route_id>/delete", methods=["POST", "DELETE"])
@login_required
def route_delete(store_id, route_id):
    """ Delete existing Route

    Return:
        Routes page
    """
    # Set Route record
    route = session.query(Route).get(route_id)

    # Test whether Route record exists
    if not route:
        flash("Could not find route with id {}".format(route_id), "danger")
        return redirect(url_for("route_get"))

    session.delete(route)
    session.commit()

    flash("Successfully deleted route", "success")
    return redirect(url_for("route_get"))


@app.route("/routes/<int:route_id>/routegroups/new", methods=["POST"])
@login_required
def route_group_add(route_id):
    """ Add new Route Group to existing Route

    Return:
        Route page
    """
    route_group = RouteGroup(route_id=route_id, route_order=99)
    session.add(route_group)
    session.commit()

    route = session.query(Route).get(route_group.route_id)

    # Renumber route order
    route.renumber_route_order()

    flash("Successfully added route group", "success")
    return redirect(url_for("route_get",
                        store_id=route.store[0].id, route_id=route_id))


@app.route("/routes/<int:route_id>/routegroups/<int:route_group_id>/delete", methods=["POST"])
@login_required
def route_group_delete(route_id, route_group_id):
    """ Delete Route Group from existing Route

    Return:
        Route page
    """
    route_group = session.query(RouteGroup).get(route_group_id)

    # Test whether RouteGroup record exists
    if not route_group:
        flash("Could not find route group record with id {}".format(route_group_id), "danger")
        return route_get(route_id=route_id)

    route = session.query(Route).get(route_group.route_id)

    session.delete(route_group)
    session.commit()

    # Renumber route order
    route.renumber_route_order()

    flash("Successfully deleted route group", "success")
    return redirect(url_for("route_get",
                        store_id=route.store[0].id, route_id=route_id))


@app.route("/lists", methods=["GET"])
@app.route("/stores/<int:store_id>/lists/new", methods=["GET"])
@app.route("/stores/<int:store_id>/lists/<list_id>", methods=["GET"])
@app.route("/stores/<int:store_id>/lists", methods=["GET"])
@login_required
def list_get(store_id=None, list_id=None):
    """ Retrieve all Lists and single List detail form

    Retrieve all Lists associated with Store

    Return:
        lists.html template
    """
    # Set all Stores for current User
    stores = session.query(UserStore).filter(UserStore.user_id == current_user.get_id()) \
        .order_by(UserStore.store_id).all()

    # If no Stores, then redirect to Stores page
    if not stores:
        flash("You do not have any stores setup. Please setup a store first.", "warning")
        return redirect(url_for("store_get"))

    # Set selected Store
    # If no selected Store or List, set to first Store and first List for user
    if not store_id and not list_id:
        store_id = session.query(UserStore.store_id).filter(UserStore.user_id == current_user.get_id())\
            .order_by(UserStore.store_id).first()
        store = session.query(Store).get(store_id)
    # If List provided, but no Store, lookup Store associated with List
    elif list_id and not store_id:
        store = session.query(Store).filter(Store.list.contains(session.query(List).get(list_id))).first()
    else:
        # Set Store object using provided id
        store = session.query(Store).get(store_id)

    # Set all Routes for current User and selected Store
    routes = session.query(Route).filter(Route.user_id == current_user.get_id(), Route.store.contains(store)) \
        .order_by(Route.id).all()

    # Set all Lists for current User and selected Store
    lists = session.query(List).filter(List.user_id == current_user.get_id(), List.store == store)\
        .order_by(List.shop_date.desc()).all()

    # Set selected List
    # New List requested
    if request.path.find("/lists/new") > -1:
        # Set as new List entry
        list = "new"
    # If Store provided, but no List, lookup first List associated with Store
    elif store_id and not list_id:
        list = session.query(List).filter(List.user_id == current_user.get_id(), List.store == store)\
            .order_by(List.shop_date.desc()).first()
    else:
        # Set List object using provided id
        list = session.query(List).get(list_id)


    # Set Route and List Items data
    list_items = {}
    route_groups = {}
    if list and list != "new":

        # Retrieve List Items associated with List (query object)
        list_items_q = session.query(ListItem).filter(ListItem.list_id == list.id)

        # If List has associated Route
        if list.route_id:

            # Retrieve related Route Groups for form input selection and List Item ordering (query object)
            route_groups_q = session.query(RouteGroup).filter(RouteGroup.route_id == list.route_id) \
                .order_by(RouteGroup.route_order)

            # Retrieve related List Items with route group order
            list_items_sq = list_items_q.subquery()
            route_groups_sq = route_groups_q.subquery()
            list_items_q = session.query(list_items_sq) \
                .outerjoin(route_groups_sq, list_items_sq.c.item_group_id == route_groups_sq.c.item_group_id) \
                .order_by(route_groups_sq.c.route_order)

            # Return Route Group rows for template
            route_groups = route_groups_q.all()

        # Return List Item rows for template
        list_items = list_items_q.all()

    # Set Item Measurements for form input selection
    item_measurements = session.query(ItemMeasurements).order_by(ItemMeasurements.id).all()

    return render_template("lists.html", view="list",
                           stores=stores, store=store,
                           routes=routes,
                           lists=lists, list=list,
                           list_items=list_items,
                           route_groups=route_groups,
                           item_measurements=item_measurements)


@app.route("/stores/<int:store_id>/lists/new", methods=["POST"])
@login_required
def list_add(store_id):
    """ Create new List

    Associate new List with Store

    Return:
        List page
    """
    data = request.form

    # Create new List
    list = List(user_id=current_user.get_id(),
                store_id=store_id)

    session.add(list)
    session.commit()

    # Update data in new record
    if not update_from_form(data, List=list.id):
        flash("Server error in creating list", "danger")
        return redirect(request.url)

    flash("Successfully created list", "success")
    return redirect(url_for("list_get",
                            store_id=list.store_id,
                            list_id=list.id))


@app.route("/stores/<int:store_id>/lists/<list_id>", methods=["PUT", "POST"])
@login_required
def list_update(store_id, list_id):
    """ Edit existing List

    Return:
        Single List page
    """
    # Return form data
    data = request.form
    # Set Route record
    list = session.query(List).get(list_id)

    # Test whether Route record exists
    if not list:
        flash("Could not find list with id {}".format(list_id), "danger")
        return redirect(url_for("list_get"))

    # Update data
    if not update_from_form(data):
        flash("Server error in updating list", "danger")
        return redirect(request.url)

    flash("Successfully updated list", "success")
    return redirect(url_for("list_get",
                            store_id=list.store_id,
                            list_id=list.id))


@app.route("/lists/<list_id>/listitems/new", methods=["POST"])
@login_required
def list_item_add(list_id):
    """ Add new List Item to existing List

    Return:
        List page
    """
    list_item = ListItem(item_name="New Item", list_id=list_id)
    session.add(list_item)
    session.commit()

    list = session.query(List).get(list_item.list_id)

    flash("Successfully added list item", "success")
    return redirect(url_for("list_get",
                            store_id=list.store_id,
                            list_id=list.id))


@app.route("/lists/<list_id>/listitems/<list_item_id>/delete", methods=["POST", "DELETE"])
@login_required
def list_item_delete(list_id, list_item_id):
    """ Delete List Item from existing List

    Return:
        List page
    """
    list_item = session.query(ListItem).get(list_item_id)
    list = session.query(List).get(list_id)

    # Test whether ListItem record exists
    if not list_item:
        flash("Could not find list item record with id {}".format(list_item_id), "danger")
        return list_get(list_id=list_id)

    session.delete(list_item)
    session.commit()

    flash("Successfully deleted list item", "success")
    return redirect(url_for("list_get",
                            store_id=list.store_id,
                            list_id=list.id))
