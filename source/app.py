'''

Copyright (C) TheOasis Interactive - All Rights Reserved
This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.

Author - Ben
Version - 1.0
'''
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_user, add_user
from pymongo import MongoClient
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from cloud import cloud_bp
from forms import DeleteForm, UploadForm
import os
import utility.usermanager as usermanager

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = "filesystem"  # Store sessions server-side
app.config["SESSION_COOKIE_SECURE"] = False  # Set to False in development (True in production)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
app.config['SECRET_KEY'] = os.urandom(24)  # This is necessary for CSRF protection
app.config['DEBUG'] = True

# Register Cloud Service
app.register_blueprint(cloud_bp, url_prefix="/cloud")

csrf = CSRFProtect(app)
Session(app)

# Routes
@app.route("/")
def home():
    return render_template("index.html") 
     # Update to your homepage template if different

## AUTH ##
@app.route("/Auth/Login", methods=["GET", "POST"])
def login():
    form = LoginForm()  # Create an instance of the form
    #print(usermanager.checkFileAccess("NewFolder"))
  
    if form.validate_on_submit():  # Automatically checks for CSRF and field validation
        username = form.username.data
        password = form.password.data
        # Fetch user from MongoDB
        user = get_user(username)
        ## Login Function
        if user and check_password_hash(user["password"], password):
            session["username"] = username          
            session["loggedIn"] = True
            session["role"] = user["role"]          
            flash("Login successful!", "success")
            return redirect(url_for("portal"))
        else:
            flash("Invalid username or password.", "danger")

    if "loggedIn" in session:
        return redirect(url_for("portal"))
    
    return render_template("login.html", form=form)  # Pass the form to the template


@app.route("/Auth/Logout")
def logout():
    # Remove the username and loggedIn from the session
    session.pop("username", None)
    session.pop("loggedIn", None)
    
    # Flash message to indicate successful logout
    flash("Logged out successfully.", "info")
    
    # Redirect to the login page after logging out
    return redirect(url_for("login"))


## Portal

@app.route("/Portal")
def portal():
    if "loggedIn" not in session:
        flash("Please log in to access the portal.", "warning")
        return redirect(url_for("login"))
    
    return render_template("portal.html")

# User Manager 
@app.route("/Accounts/Manage")
def manageAccount():
    if "loggedIn" not in session:
        flash("Please log in to access the portal.", "warning")
        return redirect(url_for("login"))
    
    return render_template("accounts.html")

## Tools

# Network 
@app.route("/Tools/Network")
def networkTools():
    if "loggedIn" not in session:
        flash("Please log in to access the portal.", "warning")
        return redirect(url_for("login"))
    
    return render_template("network.html")

# Software

@app.route("/Software/Cloud", methods=["GET", "POST"])
def softwareCloud():
    if "loggedIn" not in session:
        flash("Please log in to access the portal.", "warning")
        return redirect(url_for("login"))    
    return redirect(url_for("Cloud.list_files")) 


## App Functions ##

# DB #
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://APIUSER:9JnmArYfLRB9oYAs@developmentserver.0jw3v.mongodb.net/?retryWrites=true&w=majority&appName=DevelopmentServer")  # Default to local MongoDB if not set

def get_db():
    """
    Returns a MongoDB database connection using the Mongo URI.
    """
    client = MongoClient(MONGO_URI)
    db = client.get_database("oasis")  
    return db

def get_user(username):
    """
    Fetch a user from the database by username.
    """
    db = get_db()
    user = db.users.find_one({"username": username})  # Assuming "users" is the collection name
    return user

def getAccessLevel(username):
    # Find the user document by username
    db = get_db()
    user = db.find_one({"username": username})
    
    if user:
        # Access levels are stored as a list in the 'access_levels' field
        access_levels = user.get('accessLevel', [])  # Default to an empty list if not found
        return access_levels
    else:
        return []  # Return an empty list if the user doesn't exist
    

if __name__ == "__main__":
    app.run(debug=True)


