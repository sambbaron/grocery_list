""" Application Views """

from flask import render_template, redirect, url_for
from flask.ext.login import current_user

from . import app
from .database import session
from .models import List, Route

@app.route("/")
def index():
    """ App entry routing
    Login or go to page with data
    """

    # If no user, redirect to login
    if current_user.is_anonymous() == True:
        return redirect(url_for("login_get"))
    # Redirect to Lists if exist
    elif session.query(List).filter("user_id" == current_user).first() is not None:
        return redirect(url_for("/user/" + current_user + "/lists"))
    # Redirect to Routes if exist
    elif session.query(Route).filter("user_id" == current_user).first() is not None:
        return redirect(url_for("/user/" + current_user + "/routes"))
    # Else redirect to Stores
    else:
        return redirect(url_for("/user/" + current_user + "/stores"))

@app.route("/login", methods=["GET"])
def login_get():
    """ Returns: Login page """
    return render_template("login.html")