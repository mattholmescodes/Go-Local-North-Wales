import os

import re
import requests
import sqlite3
con = sqlite3.connect("glnw.db", check_same_thread=False)
cur = con.cursor()
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required #lookup, gbp
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)



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
            flash("Error! Please provide username", "danger")
            return redirect("/login")

        if not password:
            flash("Error! Please provide password", "danger")
            return redirect("/login")

        # Query database for username
        row = cur.execute("SELECT id, hash FROM users WHERE username=?", (username,)).fetchone()

        if not row or not check_password_hash(row[1], password):  # hash is at index 1
            flash("Error! Invalid username and/or password, please try again", "danger")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = row[0]

        flash("Login successful!", "success")
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
            flash("Error! Passwords don't match, please try again.", "danger")
            return redirect("/register")
        
        if not postcode_format(postcode):
            flash("Error! Invalid Postcode format.", "danger")
            return redirect("/register")
        
        if not postcode_api(postcode):
            flash("Error! Postcode does not exist.", "danger")
            return redirect("/register")

        if not all([username, password, confirmation, county, postcode, email]):
            flash("Error! One or more fields are blank", "danger")
            return redirect("/register")

        row = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if row:
            flash("Error! Username already exists.", "danger")
            return redirect("/register")

        # Insert new user
        cur.execute(
            "INSERT INTO users (username, email, hash, county, postcode) VALUES (?, ?, ?, ?, ?)",
            (username, email, generate_password_hash(password), county, postcode),
        )
        con.commit()

        # Retrieve new user's ID and log them in
        session["user_id"] = cur.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]

        flash("Registration successful! You are now logged in.", "success")
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