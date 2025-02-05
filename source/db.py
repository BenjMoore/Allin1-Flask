import os
import logging
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
