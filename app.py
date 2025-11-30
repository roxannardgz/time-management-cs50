from flask import Flask, render_template, request
from markupsafe import escape
from datetime import datetime

# Configure application
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sessions")
def sessions():
    return render_template("sessions.html")


@app.route("/activities")
def activities():
    return render_template("activities.html")