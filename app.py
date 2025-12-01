from flask import Flask, render_template, request, flash, session, redirect, url_for
from markupsafe import escape
from datetime import datetime

# Configure application
app = Flask(__name__)
app.secret_key = "dev"
app.config["TEMPLATES_AUTO_RELOAD"] = True

USERS = {"demo": "demo123"}



# Configure database


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
        pass

    # User reached via GET
    else:
        return render_template("signup.html")


@app.route("/login", methods=['GET', 'POST'])
def login():

    # Forget any user_id
    session.clear()

    # User reached via POST
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "warning")
            return render_template("login.html"), 400

        expected_password = USERS.get(username)
        if expected_password is None or expected_password != password:
            flash("Invalid username or password.", "danger")
            return render_template("login.html"), 401

        session["user"] = username
        flash("Logged in successfully.", "success")
        return redirect(url_for("index"))
    # User reached via GET
    else:
        return render_template("login.html")


# TODO logout
#session.clear()
