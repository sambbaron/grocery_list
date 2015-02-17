""" Application Views """

from flask import render_template

from . import app

@app.route("/")
def index():
    return render_template("base.html")