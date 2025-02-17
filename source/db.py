import os
import logging
from flask import session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://APIUSER:9JnmArYfLRB9oYAs@developmentserver.0jw3v.mongodb.net/?retryWrites=true&w=majority&appName=DevelopmentServer")
client = MongoClient(MONGO_URI)
db = client["oasis"]
users_collection = db["users"]

def get_user(username):
    """
    Fetch a user from the database by username.
    """
    try:
        user = users_collection.find_one({"username": username})
        return user if user else None
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None

def add_user(username, password):
    """
    Add a new user to the database with a hashed password.
    """
    try:
        hashed_password = generate_password_hash(password)
        users_collection.update_one(
            {"username": username},
            {"$setOnInsert": {"password": hashed_password}},
            upsert=True
        )
        logging.info(f"User '{username}' added successfully.")
        return True
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        return False
    
def get_file_access(username):
    """
    Retrieve the list of fileAccess for a given user.
    """
    try:
        user = users_collection.find_one({"username": username}, {"_id": 0, "fileAccess": 1})
        if user and "fileAccess" in user:
            return user["fileAccess"]
        return []
    except Exception as e:
        logging.error(f"Error retrieving file access: {e}")
        return []

def add_file_access(username, new_entry):
    """
    Add a new entry to the fileAccess list for a given user.
    """
    try:
        users_collection.update_one(
            {"username": username},
            {"$addToSet": {"fileAccess": new_entry}}
        )
        logging.info(f"Added '{new_entry}' to fileAccess for user '{username}'.")
        return True
    except Exception as e:
        logging.error(f"Error adding file access: {e}")
        return False


def setAccessLevel(level):
    """
    Add a new access level to the user's accessLevel list.
    """
    username = session.get("username")
    if not username:
        logging.error("No user is logged in.")
        return False

    try:
        users_collection.update_one(
            {"username": username},
            {"$addToSet": {"accessLevel": level}}  # Ensures no duplicate entries
        )
        logging.info(f"Added access level '{level}' for user '{username}'.")
        return True
    except Exception as e:
        logging.error(f"Error setting access level: {e}")
        return False

def getAccessLevel(username):
    # Find the user document by username
    user = db.find_one({"username": username})
    
    if user:
        # Access levels are stored as a list in the 'access_levels' field
        access_levels = user.get('accessLevel', [])  # Default to an empty list if not found
        return access_levels
    else:
        return []  # Return an empty list if the user doesn't exist
    