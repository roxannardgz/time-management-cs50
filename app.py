from flask import Flask, render_template, request, flash, session, redirect, url_for, g
from datetime import datetime
from functools import wraps

from helpers import get_db, close_db, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import Markup


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
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()


# Show home page: index
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sessions")
def sessions():
    return render_template("sessions.html")


@app.route("/activities")
def activities():
    return render_template("activities.html")



# TODO create account
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
            # flash("Username already taken, please try a different one.", "warning")
            #flash(Markup('Email already registered. Try a different one or <a href="/login" class="alert-link">Log in</a> instead.'), "warning")
            flash(Markup(f'Email already registered. Try a different one or <a href="{url_for("login")}" class="alert-link">Log in</a> instead.'), "warning")

            return redirect(url_for('signup'))
    

    # User reached via GET
    else:
        return render_template("signup.html")





@app.route("/login", methods=['GET', 'POST'])
def login():

    # User reached via POST
    if request.method == "POST":
        pass

    # User reached via GET
    else:
        return render_template("login.html")


# TODO logout
#session.clear()




