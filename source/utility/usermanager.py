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
from db import *
from flask import session

####### FILE ACCESS #######

def checkFileAccessLevel(filepath):
    """
    Check if the current user has a specific access level.
    """
    username = session.get("username")
    user = get_file_access(username)
    print(filepath in user)  # Get the user object
    return filepath in user # Check if the level exists

def setFileAccess(filepath):
    """
    Add a new file path to the fileAccess list for the current user.
    """
    username = session.get("username")
    if not username:
        logging.error("No user is logged in.")
        return False
    add_file_access(username, filepath)
    

############################

def checkAccessLevel(level):
    """
    Check if the current user has a specific access level.
    """
    username = session.get("username")
    if not username:
        logging.error("No user is logged in.")
        return False
    # Get the user object
    user_access_levels = getAccessLevel()  # Retrieve access levels
    return level in user_access_levels  # Check if the level exists


def checkRole(role):
    user = session.get("username")
    userInfo = get_user(user)
    actualRole = userInfo["role"]
    print(role in actualRole)
    return role in actualRole

def setUserRole(role):
    return setRole(role)



