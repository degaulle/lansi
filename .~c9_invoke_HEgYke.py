from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from flask import jsonify
from functools import wraps

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function



@app.route("/")
def main():
    """Home page."""
    return render_template("main.html")
    
@app.route("/home")
@login_required
def index():
    """Index for user accounts."""
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    if request.method == "POST":
        
        # queries database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        
        # checks if username is available
        if not request.form.get("username") or len(rows) == 1:
            return apology("username taken")
        
        # checks if password can be used
        elif not request.form.get("password") or not request.form.get("password_again") or request.form.get("password") != request.form.get("password_again"):
            return applogy("invalid password")
    
        # encrypts password
        hash = pwd_context.encrypt(request.form["password"])
    
        # adds username and hashed password into database
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :password)", username=request.form["username"], password=hash)
        
        # redirects user to home page
        return redirect(url_for("index"))
    
    # returns user to the same register page
    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
        
@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("main"))
    
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # enters uploaded essay into database table 'essays'
        db.execute("INSERT INTO essays (id, text) VALUES(:user_id, :essay_text)", user_id=session.get("user_id"), essay_text=request.form.get("essay_text"))
        
        # redirects user to upload survey form
        return render_template("upload_form.html")
    else:
        return render_template("upload.html")
        
@app.route("/upload/form", methods=["POST"])
@login_required
def upload_form():
    
    # enters survey respone into database table 'essays'
    db.e
    
    return render_template("index.html")
    
@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    if request.method == "POST":
        pass
    else:
        return render_template("messages.html")
        
@app.route("/account", methods =["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        pass
    else:
        return render_template("account.html")