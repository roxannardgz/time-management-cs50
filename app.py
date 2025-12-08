from flask import Flask, render_template, request, flash, session, redirect, url_for, g
from datetime import datetime
from functools import wraps

from helpers import get_db, close_db, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import Markup

from config import CATEGORIES

import traceback



# Configure application
app = Flask(__name__)
app.secret_key = "dev"
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Database file path
app.config["DATABASE"] = "time_management.db"


# Register teardown
app.teardown_appcontext(close_db)


# ChatGPT
@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

@app.before_request
def required_setup_if_needed():
    if g.get("user") is None:
        return
    
    if g.user["setup_completed"]:
        return
    
    allowed_endpoints = {
        "activities",
        "logout",
        "login",
        "signup",
        "static",
        "index"
    }

    if request.endpoint not in allowed_endpoints:
        return redirect(url_for("activities"))



@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Show home page: index
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sessions")
def sessions():
    return render_template("sessions.html")


@app.route("/activities", methods=["GET", "POST"])
def activities():
    # User reached via POST
    if request.method == "POST":
        
        return redirect(url_for("dashboard"))

    # User reached via GET
    return render_template("activities.html", categories=CATEGORIES)




# Create account
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Sign user up"""

    # User reached via POST
    if request.method == "POST":
        name = request.form.get("name").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")

        # Validation
        if not name or not email or not password:
            flash("All fields are required.")
            return render_template("signup.html")
        
        # Hash password
        hash = generate_password_hash(password)

        # Open db
        db = get_db()

        # Insert new user into database
        try:
            db.execute(
                "INSERT INTO users (name, email, hash) \
                VALUES (?, ?, ?)", (name, email, hash)
            )
            db.commit()
        except Exception:
            flash(Markup(f'Email already registered. Try a different one or <a href="{url_for("login")}" class="alert-link">Log in</a> instead.'), "warning")
            return redirect(url_for('signup'))
        return redirect(url_for("login"))
    

    # User reached via GET
    else:
        return render_template("signup.html")


# Log in to dashboard
@app.route("/login", methods=['GET', 'POST'])
def login():
    """Log user in"""

    # User reached via POST
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password")

        # Input validation
        if not email or not password:
            flash("All fields are required.", "warning")
            return render_template("login.html")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

        # If email not in db or password is incorrct
        if user is None or not check_password_hash(user['hash'], password):
            flash("Invalid email and/or password. Please try again.", "warning")
            return render_template("login.html")
        
        # Log in user
        session.clear()
        session["user_id"] = user["user_id"]

        return redirect(url_for("dashboard"))
            
    # User reached via GET
    return render_template("login.html")


# Dashboard and user activity
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")



# TODO logout
@app.route("/logout")
def logout():
    """Log user out"""
    
    # Forget any session data
    session.clear()

    # Redirect the user to the main page
    return redirect(url_for("index"))






