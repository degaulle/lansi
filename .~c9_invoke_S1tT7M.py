from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from flask import jsonify
from functools import wraps
from flask_mail import Mail, Message

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

#add mailserver to flask
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'peerifybot@gmail.com'
app.config['MAIL_PASSWORD'] = 'cs50peerify'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
    
    # queries for the number of essays submitted user
    essay_text = db.execute("SELECT text FROM essays WHERE id=:user_id", user_id=session.get("user_id"))
    
    # number of user's essay entries
    essay_number = len(essay_text)
    return render_template("index.html", essay_number=essay_number)

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
            return apology("invalid password")
    
        # encrypts password
        hash = pwd_context.encrypt(request.form["password"])
    
        # adds username and hashed password into database
        db.execute("INSERT INTO users (name, username, hash) VALUES(:name, :username, :password)", name=request.form["name"], username=request.form["username"], password=hash)
        
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        
        name = request.form.get("name")
        initial = "";
        if  name[0] == " ":
                initial += name[0].upper() + " "
        for c in range (2, len(name)+1): 
            if name[c-1] == " ":
                initial += name[c].upper() + " "
        
        db.execute("INSERT INTO users (initial) VALUES (:initials)", initials=initial)
        
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
        session["user_email"] = rows[0]["username"]

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
    
    # queries for the maximum value of essay_id
    essay_id = db.execute("SELECT MAX(essay_id) from essays")
    
    # enters survey respone into database table 'essays'
    db.execute("UPDATE essays SET date=:date, topic=:topic, peer_topic=:peer_topic WHERE essay_id=:essay_id", 
    date=request.form.get('date'), topic=request.form.get("user_category"), peer_topic=request.form.get("peer_category"), essay_id=essay_id[0]['MAX(essay_id)'])
    
    msg.html = essay_
    msg = Message('Peerify | Your Essay Has Been Submitted', sender = 'peerifybot@gmail.com', recipients = [session["user_email"]])
    essay_text = db.execute("SELECT text FROM essays WHERE essay_id = :essay_id", essay_id = essay_id[0]['MAX(essay_id)'])
    msg.html = "<p>Congratulations, your essay was successfully submitted! Here are the details we received from you:</p>" + \
    "<p>Requested date: " + request.form.get('date') + "</p>" + \
    "<p>Subject of Essay: " + request.form.get("user_category") + "</p>" + \
    "<p>Preferred Subject to Edit: " + request.form.get("peer_category") + "</p>" + \
    "<p>Text of Essay:</p>" + \
    essay_text[0]['text'] + \
    "<br><p>You should receive a response within your specified time interval. Don't forget to edit your paired essay, too!</p>"
    "<p>With Love,</p>" + "<p>Peerify Bot</p>"
    mail.send(msg)
    
    
    return redirect(url_for("index"))

@app.route("/essays", methods=["GET", "POST"])
@login_required
def essays():
    if request.method == "GET":
        essay_number = request.args.get('number')
        essay_text = db.execute("SELECT text FROM essays WHERE essay_id = :essay_id", essay_id=essay_number)
        return render_template("essays.html", essay_text=essay_text[0]['text'])
    else:
        return render_template("essays.html")
    
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
        
@app.route("/password", methods =["GET", "POST"])
@login_required
def password():
    if request.method == "POST":

        #confirm that user has entered a password into form 
        if not request.form.get("curr_password"):
            return apology("Enter a password")
            
        elif not request.form.get("new_password"):
            return apology("Enter a password")
            
        elif not request.form.get("new_password_again"):
            return apology("Enter a password")
        
        #select user's session from the database users
        user_info = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session.get("user_id"))
    
        # checks if entered new passwords match
        if request.form.get("new_password") == request.form.get("new_password_again"):
            # hashes the new password
            hash_pw = pwd_context.encrypt(request.form["new_password"])
            db.execute("UPDATE users SET hash = :new_password WHERE id = :user_id", new_password=hash_pw, user_id=session.get("user_id"))
        else:
            return apology("passwords do not match")
        
        #redirect to account page
        return redirect(url_for("account"))
    else:
        return render_template("password.html")