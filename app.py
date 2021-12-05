import googlemaps
import pprint
import time

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *
from datetime import datetime

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# Configure application
app = Flask(__name__)
app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

gmaps = googlemaps.Client(key = app.config['GOOGLE_KEY'])

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///apptivism.db")

# Verification function (used a few times throughout and inspired by Pretty Printed's YouTube)
def send_verification(email): 
    token = s.dumps(email)

    msg = Message('Please confirm your Apptivism account email address.', sender=app.config["MAIL_USERNAME"], recipients=[email])

    link = url_for('confirm_email', token=token, _external=True)

    msg.html = 'Click <a href="{}">here</a> to confirm your email. This link expires in 24 hours.'.format(link)

    mail.send(msg)

    return

@app.route("/")
def index():
    # Ensure user is logged in
    if session.get('user_id'):
        # Redirect to organize page
        return redirect("/organize")
    else:
        # Redirect to log in page
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
# log user in
def login():

    # clear any existing sessions
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return "Must provide username."

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "invalid username and/or password"

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to organize page
        return redirect("/organize")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
# registers new account
def register():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", username_error="Must provide username.", states=states)

        # Ensure valid email was submitted
        elif not request.form.get("email"):
            return render_template("register.html", email_error="Must provide email address.", states=states)

        elif "@" not in request.form.get("email") or "." not in request.form.get("email"):
            return render_template("register.html", email_error="Must provide valid email address.", states=states)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", password_error="Must provide password.", states=states)

        # Store username and password as variables
        username = str(request.form.get("username"))
        password = str(request.form.get("password"))
        email = str(request.form['email'])

        # Ensure passwords match
        if password != request.form.get("confirmation"):
            return render_template("register.html", confirmation_error="Passwords do not match.", states=states)

        # Ensure password is at least 8 characters long & contains at least one digit
        contains_digit = False

        for char in password:
            if char.isdigit():
                contains_digit = True
                break

        if len(password) < 8 or contains_digit == False:
            return render_template("register.html", password_error="Password must be at least 8 characters long & contain at least one digit.", states=states)

        #Ensure email isnt already taken
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        if len(rows) != 0:
            return render_template("register.html", email_error="Sorry, that email is already in use.", states=states)

        # Ensure username isnt already taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 0:
            return render_template("register.html", username_error="Sorry, that username is already taken.", states=states)
        
        # Ensure valid home address was submitted
        if not request.form.get("street") or not request.form.get("city") or not request.form.get("state") or not request.form.get("zip"):
            return render_template("register.html", address_error="Please enter a valid street address.", states=states)

        address = request.form.get("street") + ", " + request.form.get("city") + ", " + request.form.get("state") + ", " + request.form.get("zip")
        
        try:
            geocode_result = gmaps.geocode(address)
        except:
            return render_template("register.html", address_error="Please enter a valid street address.", states=states)

        # Store username, email, hashed password, and the longitude and latitude of user's address in database
        hashed_pass = generate_password_hash(password)

        db.execute("INSERT INTO users (username, email, hash, lat, lng) VALUES(?, ?, ?, ?, ?)", username, email, hashed_pass, geocode_result[0]["geometry"]["location"]["lat"], geocode_result[0]["geometry"]["location"]["lng"])

        # Log user in upon registration and start a session for them
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Send confirmation email
        send_verification(email)

        return render_template("email_sent.html", username=username, email=email)

    else:
        return render_template("register.html", states=states)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/confirm_email/<token>')
# Confirms new user's email address
def confirm_email(token):
    try:
        # Only confirm email address if the user clicked the link within 24 hours of it being sent
        s.loads(token, max_age = 86400)
    except SignatureExpired:
        return render_template("expired.html")
    return redirect("/confirmed")

@app.route('/confirmed', methods=["GET", "POST"])
# Upon confirmation, allows user to finish setting up their account
def confirmed():
    if request.method == "POST":
        # Ensure user selected at least one social issue
        if not request.form.getlist('passions'):
            return render_template("confirmed.html", selection_error="Please pick at least one passion." )
        
        # Find out which social issues the user said they were passionate about
        passions = request.form.getlist('passions')
        
        # Store them in the passion database
        for passion in passions:
            db.execute("INSERT INTO passions (passion, userID) VALUES(?, ?)", passion, session["user_id"])
        
        return redirect("/organize")
    else:
        # Ensure users can't access this page a second time (resulting in duplicate passion submissions)
        if db.execute("SELECT confirmed FROM users WHERE id =?", session["user_id"])[0]["confirmed"] == "true":
            return redirect("/organize")

        # Confirm email address by updating database
        db.execute("UPDATE users SET confirmed = ? WHERE id = ?", "true", session["user_id"])
        
        return render_template("confirmed.html")

@app.route('/verification_failure')
# Resends confirmation email if user tries to access Apptivism's content without verifying
def ver_fail():
    email = db.execute("SELECT email FROM users WHERE id = ?", session["user_id"])[0]["email"]
    
    send_verification(email)

    return render_template("verification_failure.html")

@app.route('/resend_requested')
# Resends confirmation email upon user's request
def res_req():
    email = db.execute("SELECT email FROM users WHERE id = ?", session["user_id"])[0]["email"]
    
    send_verification(email)

    return render_template("resend_requested.html")

@app.route("/organize", methods=["GET", "POST"])
# Allows user to organize a protest
def organize():
    #Ensure user is logged in & verified
    if not session.get('user_id'):
        return redirect('/login')
    elif db.execute("SELECT confirmed FROM users WHERE id =?", session["user_id"])[0]["confirmed"] == "false":
        return redirect('/verification_failure')

    # Acquire user's passions
    passions_dict = db.execute("SELECT passion FROM passions WHERE userID = ?", session["user_id"])
    passions = []
    for passion in passions_dict:
        passions.append(passion['passion'])

    if request.method == "POST":
        # Ensure user selected an issue to protest
        if not request.form.get("passion"):
            return render_template("organize.html", passion_error="Please select an issue to protest.", passions=passions, states=states)
        
        # Ensure valid venue address was submitted
        if not request.form.get("street") or not request.form.get("city") or not request.form.get("state") or not request.form.get("zip"):
            return render_template("organize.html", venue_error="Please enter a valid venue location.", passions=passions, states=states)

        venue = request.form.get("street") + ", " + request.form.get("city") + ", " + request.form.get("state") + ", " + request.form.get("zip")

        try:
            geocode_result = gmaps.geocode(venue)
        except:
            return render_template("organize.html", venue_error="Please enter a valid venue location.", passions=passions, states=states)

        # Ensure date & time were submitted
        if not request.form.get("start_datetime"):
            return render_template ("organize.html", time_error="Please enter a protest start time.", passions=passions, states=states)

        # Convert current datetime into integer list of numbers going year-month-day-hour-minute
        now = str(datetime.now()).split()

        now = time_splicer(now)

        # Convert protest datetime into integer list of numbers going year-month-day-hour-minute
        start_datetime = request.form.get("start_datetime").split('T')

        start_datetime = time_splicer(start_datetime)
        
        # Ensure the submitted date time isn't before "now"
        i = 0
        valid_start = True
        while i < 5:
            if start_datetime[i] < now[i]:
                valid_start = False
                break
            else:
                i += 1

        if valid_start == False:
            return render_template("organize.html", time_error="Unless you're a timetraveler, please enter a time that has not yet passed.", passions=passions, states=states)

        # Store protest info in database
        issue = request.form.get("passion")
        venue_location = gmaps.geocode(venue)
        venue_lat = venue_location[0]["geometry"]["location"]["lat"]
        venue_lng = venue_location[0]["geometry"]["location"]["lng"]
        start = "On " + start_datetime[1] + "/" + start_datetime[2] + "/" + start_datetime[0] + ", at " + start_datetime[3] + ":" + start_datetime[4]

        db.execute("INSERT INTO protests (issue, lat, lng, start, organizerID) VALUES(?, ?, ?, ?, ?)", issue, venue_lat, venue_lng, start, session['user_id'])

        return render_template("organized.html", issue=issue)
    
    else:
        return render_template("organize.html", passions=passions, states=states)

@app.route("/find", methods=["GET", "POST"])
# Allows users to find relevant protests near them
def find():
    #Ensure user is logged in & verified
    if not session.get('user_id'):
        return redirect('/login')
    elif db.execute("SELECT confirmed FROM users WHERE id =?", session["user_id"])[0]["confirmed"] == "false":
        return redirect('/verification_failure')

    if request.method=="POST":
        # Ensure proximity preference has been indicated
        if not request.form.get("proximity"):
            return render_template("find.html", proximity_error="Please indicate a preferred proximity.")

        # Format user's origin
        origin_raw = db.execute("SELECT lat, lng FROM users WHERE id = ?", session["user_id"])[0]

        origin = [(origin_raw["lat"], origin_raw["lng"])]

        # Acquire user's proximity preference
        proximity = request.form.get("proximity")
        protests_raw = db.execute("SELECT issue, lat, lng, start FROM protests WHERE issue IN (SELECT passion FROM passions WHERE userID = ?)", session["user_id"])

        # Present protests in accordance with user's proximity preference
        if proximity == "Any distance":
            
            protests = find_protests(origin, protests_raw)

            return render_template("found.html", protests=protests)
        
        else:
            # Convert proximity into usable intger value
            proximity = int(proximity.split()[0])

            protests = find_protests(origin, protests_raw, proximity)

            return render_template("found.html", protests=protests)
    else:
        return render_template("find.html")







