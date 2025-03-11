import os

import re
import requests
import sqlite3
con = sqlite3.connect("glnw.db", check_same_thread=False)
cur = con.cursor()
from flask import Flask, flash, redirect, render_template, request, session
from flask_session.__init__ import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required #lookup, gbp



# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = "sqlite:///glnw.db"


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("Error! Please provide username", 403)

        if not password:
            return apology("Error! Please provide password", 403)

        # Query database for username
        row = cur.execute("SELECT id, hash FROM users WHERE username=?", (username,)).fetchone()

        if row is None or not check_password_hash(row[1], password):  # hash is at index 1
            return apology("Error! Invalid username and/or password, please try again", 403)

        # Remember which user has logged in
        session["user_id"] = row[0]

        return redirect("/")

    return render_template("login.html")

@app.route("/")
@login_required
def index():
    "Homepage"

    return render_template("index.html")

def postcode_format(postcode):
    """Check if the postcode follows a strict UK format using regex"""
    pattern = r"^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$"
    return bool(re.match(pattern, postcode.upper().strip()))  # Convert to uppercase & remove spaces

def postcode_api(postcode):
    """Check if the postcode exists using an API"""
    try:
        response = requests.get(f"https://api.postcodes.io/postcodes/{postcode}/validate")
        response.raise_for_status()  # Raise an error if the request fails
        data = response.json()
        return data.get("result", False)  # True if postcode is valid, False otherwise
    except requests.RequestException:
        return False  # If API fails, reject the postcode

@app.route('/register', methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        county = request.form.get("county")
        postcode = request.form.get("postcode").strip().upper()

        if password != confirmation:
            return apology("Error! Passwords don't match, please try again.", 400)
        
        if not postcode_format(postcode):
            return apology("Error! Invalid Postcode format.", 400)
        
        if not postcode_api(postcode):
            return apology("Error! Postcode does not exist.", 400)

        if not all([username, password, confirmation, county, postcode, email]):
            return apology("Error! One or more fields are blank", 400)

        row = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if row:
            return apology("Error! Username already exists.", 400)

        # Insert new user
        cur.execute(
            "INSERT INTO users (username, email, hash, county, postcode) VALUES (?, ?, ?, ?, ?)",
            (username, email, generate_password_hash(password), county, postcode),
        )
        con.commit()

        # Retrieve new user's ID and log them in
        session["user_id"] = cur.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]

        return redirect("/")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/buy")
@login_required
def buy():
    return render_template("buy.html")

@app.route("/sell")
@login_required
def sell():
    return render_template("sell.html")