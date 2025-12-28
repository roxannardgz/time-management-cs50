import sqlite3

from flask import g, current_app, request, redirect, url_for
from functools import wraps


# ChatGPT: recommended Flask pattern
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# https://flask.palletsprojects.com/en/stable/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# From C$50 Finance - Problem Set 9
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function



def seconds_to_hhmm(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(hours):02d}:{int(minutes):02d}"

