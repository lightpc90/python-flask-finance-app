import os
from unittest import result

from cs50 import SQL
from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        buy_query = request.form.get("buy")
        share = request.form.get("share")
        results = lookup(buy_query)
        if not buy_query or not results:
            return apology('todo')
        return render_template("buy.html", results=results)
    else:
        return render_template("buy.html")
    ##return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return render_template("history.html")
    ##return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "post":
        query = request.form.get("symbol")
        results = lookup(query)
        if results or query:
            return render_template("", results=results, query=query)
        else:
            get_flashed_messages("Symbol not valid!")
            return render_template("quoted.html", message='no query, no result')
    else:
        return render_template("buy.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        hashed_password = generate_password_hash(request.form.get("password"))
        confirm_password = request.form.get("confirm_password")
        if username and hashed_password and confirm_password:
            db.execute("INSERT INTO users (username, hash) values (?, ?)", username, hashed_password)
            flash("You have successfully Registered!")
            return redirect("/login")
        # when a user tries to register without filling the form completely
        return apology("Please, fill the form to register", 403)
    # when a user tries to use get
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == 'post':
        query = request.form.get("symbol")
        symbol_result = lookup(query)
        return render_template("index.html", symbol_result=symbol_result)
    return render_template("sell.html")
        ##return apology("TODO")
