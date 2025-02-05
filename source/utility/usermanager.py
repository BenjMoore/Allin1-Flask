'''
User manager v1 
Functions
> Check User File Access
> Set User File Access
> Check User Access Level
> Set User Access Level
> Check Role
> Set Role
'''
from flask import session
from app import get_db, get_user

def checkFileAccess(filepath):
    username = session.get("username")
    user = get_user(username)  # Get the user object
    usersFiles = user.get("fileAccess", [])  # Retrieve the list of file paths
    return filepath in usersFiles  # Check if the file exists in the list


def setFileAccess():
    return

def checkAccessLevel():
    return

def setAccessLevel():
    return

def checkRole():
    return

def setRole():
    return



