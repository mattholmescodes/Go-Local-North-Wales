import os

import re
import requests
import sqlite3
con = sqlite3.connect("glnw.db", check_same_thread=False)
cur = con.cursor()
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required #lookup, gbp
from math import radians, cos, sin, asin, sqrt


# Configure application
app = Flask(__name__)



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = "sqlite:///glnw.db"

GOOGLE_MAPS_API_KEY = "AIzaSyAIsztPFdHFaAUxo1hqEWK3jCkdvY5wfD8"

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in with specific functionalities based on user type"""
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
        row = cur.execute("SELECT id, hash, user_type FROM users WHERE username=?", (username,)).fetchone()

        if not row or not check_password_hash(row[1], password):
            flash("Error! Invalid username and/or password, please try again", "danger")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = row[0]
        session["user_type"] = row[2]

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
def get_coordinates(postcode):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={postcode}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        lat, lng = location["lat"], location["lng"]
        print(f"Coordinates for {postcode}: {lat}, {lng}")  # Debugging
        return float(lat), float(lng)  # Ensure they are floats
    
    print(f"Error fetching coordinates for {postcode}: {data}")  # Debugging
    return None

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two points using coordinates"""
    """Taken from https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points/4913653#4913653"""

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

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
        user_type = request.form.get("user_type")

        if password != confirmation:
            flash("Error! Passwords don't match, please try again.", "danger")
            return redirect("/register")
        
        if not postcode_format(postcode):
            flash("Error! Invalid Postcode format.", "danger")
            return redirect("/register")
        
        if not postcode_api(postcode):
            flash("Error! Postcode does not exist.", "danger")
            return redirect("/register")

        if not all([username, password, confirmation, county, postcode, email, user_type]):
            flash("Error! One or more fields are blank", "danger")
            return redirect("/register")

        row = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if row:
            flash("Error! Username already exists.", "danger")
            return redirect("/register")

        # Insert new user
        cur.execute(
            "INSERT INTO users (username, email, hash, county, postcode, user_type) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, generate_password_hash(password), county, postcode, user_type),
        )
        con.commit()

        # Retrieve new user's ID and log them in
        session["user_id"] = cur.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]
        session["user_type"] = user_type

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

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        product = request.form.get("product").strip()
        buyer_postcode = cur.execute("SELECT postcode FROM users WHERE id=?", (session["user_id"],)).fetchone()[0]
        print(f"Buyer postcode: {buyer_postcode}")

        buyer_coords = get_coordinates(buyer_postcode)
        print(f"Buyer Coordinates: {buyer_coords}")
        if not buyer_coords:
            flash("Invalid postcode!", "danger")
            return redirect("/buy")

        # Fetch sellers selling the product
        sellers = cur.execute("""
            SELECT transactions.id, transactions.postcode, transactions.product, transactions.price, users.username, users.email 
            FROM transactions 
            JOIN users ON transactions.user_id = users.id 
            WHERE transactions.product=?
        """, (product,)).fetchall()

        results = []
        for seller in sellers:
            seller_postcode = seller[1]
            seller_coords = get_coordinates(seller_postcode)
            print(f"Seller Coordinates: {seller_coords}")

            if not seller_coords:
                continue

            distance = haversine(
                float(buyer_coords[1]), float(buyer_coords[0]),  # Ensure float values
                float(seller_coords[1]), float(seller_coords[0]) 
            )

            results.append({
                "username": seller[4],  
                "product": seller[2],  
                "price": round(float(seller[3]), 2),  # Ensure price is stored as a float  
                "postcode": seller_postcode,
                "distance": round(distance, 2),
                "email": seller[5]
            })

        results.sort(key=lambda x: x["distance"]) 

        return render_template("buy.html", results=results)

    return render_template("buy.html", results=None)

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session["user_id"]

    # Fetch seller's postcode from users table
    seller_postcode = cur.execute("SELECT postcode FROM users WHERE id=?", (user_id,)).fetchone()[0]

    if request.method == "POST":
        product = request.form.get("product").strip()
        price = request.form.get("price")
        quantity = request.form.get("quantity")

        if not product or not price or not quantity:
            flash("All fields are required!", "danger")
            return redirect("/sell")

        # Insert into transactions table
        cur.execute(
            "INSERT INTO transactions (user_id, product, price, postcode, quantity) VALUES (?, ?, ?, ?, ?)",
            (user_id, product, price, seller_postcode, quantity)
        )
        con.commit()

        flash("Product listed successfully!", "success")
        return redirect("/sell")

    # Fetch seller's current listings
    listings = cur.execute("SELECT product, price, quantity, postcode, timestamp FROM transactions WHERE user_id=?",(user_id,)).fetchall()

    return render_template("sell.html", listings=listings)

@app.route("/about")
@login_required
def about():
    "Homepage"

    return render_template("about.html")