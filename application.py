import os
import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, usd
import json

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Loading Database
conn = sqlite3.connect("easyshop.db", check_same_thread=False)
db = conn.cursor()

# Loading Items from Database
ITEMS_CURSOR = db.execute("SELECT * FROM items")

ITEMS_LIST = []
COLS = ['uniq_id','name','product_category_tree','retail_price','price','image_link','description','product_rating','overall_rating','brand','product_specifications']
for row in ITEMS_CURSOR:
    new_val = {}
    for i in range(len(row)):
        new_val[COLS[i]] = row[i]
    ITEMS_LIST.append(new_val)

@app.route("/")
def index():
    """Show Products"""

    return render_template("index.html", items=ITEMS_LIST)

@app.route("/scan", methods=["GET", "POST"])
@login_required
def scan():
    """Scan and add item to cart"""
    
    return render_template("scan.html")

@app.route("/cart")
@login_required
def cart():
    """Show users cart"""

    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        cursor = db.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username"),))

        rows = []
        for row in cursor:
            rows.append(row)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("Invalid username or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Ensure Confirmation password was submitted
        elif not request.form.get("Cpassword"):
            return apology("Must Confirm Password", 403)

        # Checks if Password Entered is correct
        elif request.form.get("password") != request.form.get("Cpassword"):
            return apology("Passwords Not Matching", 403)

        # Query database for username
        cursor = db.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username"),))

        for row in cursor:
            if (row[1] == request.form.get("username")):
                return apology("Username already in use", 403)

        # Inserting Username and Password-Hash to database.users
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",(
                    request.form.get("username"),
                    generate_password_hash(request.form.get("password")),))

        conn.commit()

        # Query database for username
        cursor = db.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username"),))

        for row in cursor:
            if (row[1] == request.form.get("username")):
                session["user_id"] = row[0]

        return render_template("index.html", items=ITEMS_LIST)
    
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
