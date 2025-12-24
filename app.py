from flask import Flask, render_template, request, flash, session, redirect, url_for, g
from datetime import datetime
from functools import wraps

from helpers import get_db, close_db, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import Markup

from config import CATEGORIES

import traceback
import charts
import pandas as pd


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
            """
            SELECT * FROM users WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()


@app.before_request
def require_setup_if_needed():
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

# TODO; restrict access to certain pages after login (e.g landing page, signup page...)


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


@app.route("/activities", methods=["GET", "POST"])
@login_required
def activities():
    # User reached via POST
    if request.method == "POST":
        selected_categories = request.form.getlist("categories")
        selected_activities = request.form.getlist("activities") # subcategories

        # Parse selexted subcategories into a dict
        chosen_by_cat = {}
        for item in selected_activities:
            category, subcat = item.split("::", 1)
            chosen_by_cat.setdefault(category, []).append(subcat)

        # Enfore the selection of at least 5 categories
        if len(selected_categories) < 5:
            flash("Please select at least 5 categories.", "warning")
            return render_template(
                   "activities.html",
                   categories=CATEGORIES,
                   selected_categories=selected_categories,
                   selected_activities=selected_activities,
                   )
        
        # Enforce the selection of at least one subcat when a category is selected
        for cat in selected_categories:
            if cat not in chosen_by_cat or len(chosen_by_cat[cat]) == 0:
                flash(f"Please select at least one subcategory for {cat}", "warning")
                return render_template(
                    "activities.html",
                    categories=CATEGORIES,
                    selected_categories=selected_categories,
                    selected_activities=selected_activities,
                )
            
        # If valiation passes, 
        db = get_db()

        # Delete previous selection if exists **For when updating categories will be available**
        # db.execute(
        #     "DELETE FROM user_activities WHERE user_id = ?",
        #     (g.user["user_id"],)
        # )

        # save categories and subcategories to DB
        for category, subcats in chosen_by_cat.items():
            for subcat in subcats:
                db.execute(
                    "INSERT INTO user_activities (user_id, category, subcategory) \
                    VALUES (?, ?, ?)",
                    (g.user["user_id"], category, subcat)
                )

        # Update setup completed in users table
        db.execute(
            "UPDATE users SET setup_completed = 1 WHERE user_id = ?",
            (g.user["user_id"],),
        )

        db.commit()
        return redirect(url_for("dashboard"))

    # User reached via GET
    return render_template("activities.html", categories=CATEGORIES)


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
        user = db.execute(
            """SELECT * 
            FROM users 
            WHERE email=?""",
              (email,)).fetchone()

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

    db = get_db()

    # Get the categories and subcats of the user
    rows = db.execute(
        """
        SELECT category, subcategory
        FROM user_activities
        WHERE user_id = ?
        """,
        (g.user["user_id"],)
    ).fetchall()

    # Create the dict for the dropdowns
    activities_by_cat = {}
    for row in rows:
        activities_by_cat.setdefault(row["category"], []).append(row["subcategory"])

    # Load the active session (the one with null end ts)
    active_session = db.execute(
        """
        SELECT *
        FROM events
        WHERE user_id = ? AND end_ts IS NULL
        """,
        (g.user["user_id"],)
    ).fetchone()


    # User selector for dashboard view: daily or last 7 days
    period = request.args.get("period", "today")

    if period == "week":
        date_filter = """
            event_date BETWEEN DATE('now', 'localtime', '-6 days')
                            AND DATE('now', 'localtime')
        """
    else:
        date_filter = "event_date = DATE('now', 'localtime')"

    # Query for hours by category
    query = f"""
        SELECT
            category,
        SUM(total_seconds) AS total_time_spent_seconds
        FROM vw_daily_activity
        WHERE user_id = ? AND {date_filter}
        GROUP BY category
        ORDER BY total_time_spent_seconds DESC
        """

    df_by_category = pd.read_sql_query(query, db, params=(g.user["user_id"],))

    # Check if there is not data for today (if the df_today_by_category is empty)
    if df_by_category.empty:
        chart_divs = {}
        kpis = {}

        return render_template("dashboard.html", 
                           activities_by_cat=activities_by_cat, 
                           active_session=active_session,
                           period=period,
                           chart_divs=chart_divs,
                           kpis = kpis)
    
    # If there is data for today (df_today_by_category)
    # Calculate time in h for hours by category bar chart
    df_by_category["total_time_spent_hours"] = df_by_category["total_time_spent_seconds"]/3600

    # KPI cards values
    total_time_tracked = (df_by_category["total_time_spent_seconds"].sum()/3600).round(2)
    top_category = df_by_category.iloc[0]["category"]

    # Create the dict for category filter for today and validate or default to top category
    categories_available = df_by_category["category"].tolist()
    selected_category = request.args.get("category", top_category)
    if selected_category not in categories_available:
        selected_category = top_category

    # Query dates 
    query = f"""
        SELECT DISTINCT event_date
        FROM vw_daily_activity
        WHERE user_id = ? 
            AND {date_filter}
        """
    
    dates = pd.read_sql_query(query, db, params=(g.user["user_id"],))
    
    # Query for categories breakdown
    query = f"""
        SELECT    
            subcategory,
            SUM(total_seconds) AS total_time_spent_seconds
        FROM vw_daily_activity
        WHERE user_id = ? 
            AND {date_filter}
            AND category = ?
        GROUP BY subcategory
        """

    df_subcategory_breakdown = pd.read_sql_query(query, db, params=(g.user["user_id"], selected_category))

    # Calculate time in h
    df_subcategory_breakdown["total_time_spent_hours"] = df_subcategory_breakdown["total_time_spent_seconds"]/3600

    # Values for pie chart day division
    time_selected_category = df_subcategory_breakdown["total_time_spent_hours"].sum()

    # Dates in range of view
    min_date = pd.to_datetime(dates["event_date"]).min().date()
    max_date = pd.to_datetime(dates["event_date"]).max().date()

    days_in_period = (max_date - min_date).days + 1
    hours_in_period = days_in_period * 24

    # Data for category share pie
    df_category_share = pd.DataFrame({
        "label": [selected_category, "Rest of day"],
        "hours": [
            time_selected_category,
            max(0, hours_in_period - time_selected_category)
        ]
    })



    # Build chart and convert to div
    chart_today_by_category = charts.today_by_category(df_by_category)
    div_today_by_category = charts.fig_to_div(chart_today_by_category)

    chart_subcategory_breakdown = charts.subcategories_breakdown(df_subcategory_breakdown, selected_category)
    div_subcategory_breakdown = charts.fig_to_div(chart_subcategory_breakdown)

    chart_category_share = charts.category_share_donut(df_category_share)
    div_category_share = charts.fig_to_div(chart_category_share)

    
    chart_divs = {"div_today_by_category": div_today_by_category,
                    "div_subcategory_breakdown": div_subcategory_breakdown,
                    "div_category_share": div_category_share}
    kpis = {"total_time_tracked": total_time_tracked,
                    "top_category": top_category}



    # Show page
    return render_template("dashboard.html", 
                           activities_by_cat=activities_by_cat, 
                           active_session=active_session,
                           period=period,
                           categories_available=categories_available,
                           selected_category=selected_category,
                           chart_divs=chart_divs,
                           kpis = kpis)



@app.route("/sessions/start", methods=["POST"])
@login_required
def start_session():
    category = request.form.get("category")
    subcategory = request.form.get("subcategory")

    # Validation: both values are selected
    if not category or not subcategory:
        flash("Please choose a category and subcategory to start recording", "warning")
        return redirect(url_for("dashboard"))
    
    db = get_db()

    # Validation: there is no existing active session
    existing = db.execute(
        """
        SELECT event_id 
        FROM events 
        WHERE user_id = ? AND end_ts IS NULL
        """,
        (g.user["user_id"],)
    ).fetchone()

    if existing is not None:
        flash("You already have an active session. Stop it before starting a new one.", "warning")
        return redirect(url_for("dashboard"))
    
    # If validation passed
    start_ts = datetime.now().isoformat(timespec="seconds")

    db.execute(
        "INSERT INTO events (user_id, category, subcategory, start_ts) \
        VALUES (?, ?, ?, ?)",
        (g.user["user_id"], category, subcategory, start_ts)
    )
    db.commit()

    return redirect(url_for("dashboard"))


@app.route("/sessions/stop", methods=["POST"])
@login_required
def stop_session():

    db = get_db()

    active = db.execute(
        """
        SELECT event_id
        FROM events
        WHERE user_id = ? AND end_ts IS NULL
        """,
        (g.user["user_id"],)
    ).fetchone()

    if active is None:
        flash("There is no active session to stop", "warning")
        return redirect(url_for("dashboard"))
    
    end_ts = datetime.now().isoformat(timespec="seconds")

    db.execute(
        "UPDATE events SET end_ts = ? WHERE event_id = ?",
        (end_ts, active["event_id"])
    )

    db.commit()

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    """Log user out"""
    
    # Forget any session data
    session.clear()

    # Redirect the user to the main page
    return redirect(url_for("index"))

