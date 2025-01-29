import os
import shutil
from flask import Blueprint, request, render_template, send_from_directory, redirect, session, url_for, flash
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from forms import CreateFolderForm, UploadForm, DeleteForm


cloud_bp = Blueprint("Cloud", __name__)

BASE_DIR = os.path.join(os.path.dirname(__file__), "root")
os.makedirs(BASE_DIR, exist_ok=True)

######## DB ###########
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://APIUSER:Monkeyman30@developmentserver.0jw3v.mongodb.net/?retryWrites=true&w=majority&appName=DevelopmentServer")  # Default to local MongoDB if not set

def getFileAccess(username):
    # Find the user document by username
    db = get_db()
    user = db.find_one({"username": username})
    
    if user:
        # Access levels are stored as a list in the 'access_levels' field
        access_levels = user.get('fileAccess', [])  # Default to an empty list if not found
        return access_levels
    else:
        return []  # Return an empty list if the user doesn't exist

def get_db():
    """
    Returns a MongoDB database connection using the Mongo URI.
    """
    client = MongoClient(MONGO_URI)
    db = client.get_database("oasis")  
    return db
################
  
# Helper function to list the files and folders inside a directory
def list_directory(path=BASE_DIR):
    items = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        items.append({
            "name": item,
            "type": "folder" if os.path.isdir(item_path) else "file",
            "path": os.path.relpath(item_path, BASE_DIR)  # Relative path from the root
        })
    return items

@cloud_bp.route("/List", methods=["GET", "POST"])
def list_files():
    #print(getFileAccess(session["username"]))
    folder_path = request.args.get("folder", "")
    folder_full_path = os.path.join(BASE_DIR, folder_path) if folder_path else BASE_DIR

    # Form instances
    create_folder_form = CreateFolderForm()
    delete_form = DeleteForm()

    # Handle folder creation from the form
    if create_folder_form.validate_on_submit():
        folder_name = create_folder_form.folder.data.strip()
        new_folder_path = os.path.join(folder_full_path, folder_name)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            flash(f"Folder '{folder_name}' created successfully", "success")
        else:
            flash(f"Folder '{folder_name}' already exists", "error")
        return redirect(url_for("Cloud.list_files", folder=folder_path))

    # List files and folders in the current directory
    files = list_directory(folder_full_path)
    return render_template(
        "cloud.html",
        files=files,
        create_folder_form=create_folder_form,
        delete_form=delete_form,
        folder=folder_path,
    )

@cloud_bp.route("/createFolder", methods=["POST", "GET"])
def create_folder():
    folder_name = request.form.get("folder")
    folder_path = request.args.get("folder", "")
    folder_full_path = os.path.join(BASE_DIR, folder_path) if folder_path else BASE_DIR

    # Default folder name if none is provided
    if not folder_name:
        folder_name = "newfolder"

    # Check if the folder already exists and increment the name if necessary
    original_folder_name = folder_name
    counter = 1
    new_folder_path = os.path.join(folder_full_path, folder_name)

    while os.path.exists(new_folder_path):
        folder_name = f"{original_folder_name}{counter}"
        new_folder_path = os.path.join(folder_full_path, folder_name)
        counter += 1

    # Create the folder
    os.makedirs(new_folder_path)
    flash(f"Folder '{folder_name}' created successfully", "success")

    return redirect(url_for("Cloud.list_files", folder=folder_path))


@cloud_bp.route("/uploadPage", methods=["GET", "POST"])
def upload_page():
    upload_form = UploadForm()

    # Get the current folder from the URL or default to the root folder
    folder = request.args.get('folder', '')  # Get folder parameter from the query string, default to '' if not found
    
    # List all folders in the specified folder or in the root folder if no folder is selected
    base_folder = os.path.join(BASE_DIR, folder)
    folders = [f.name for f in os.scandir(base_folder) if f.is_dir()]
    
    # Default to current folder if none is selected
    if not folder:
        folder = ''  # root folder if not selected
    
    if upload_form.validate_on_submit():
        file = upload_form.file.data
        target_folder = os.path.join(BASE_DIR, folder) if folder else BASE_DIR
        os.makedirs(target_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        file.save(os.path.join(target_folder, filename))
        flash("File uploaded successfully", "success")
        return redirect(url_for("Cloud.list_files"))

    return render_template("upload_page.html", form=upload_form, folders=folders, current_folder=folder)


@cloud_bp.route("/delete_folder", methods=["POST"])
def delete_folder():
    folder = request.form.get("folder")  # Get folder path from form

    if not folder:
        flash("No folder specified!", "danger")
        return redirect(url_for("Cloud.list_files"))

    folder_path = os.path.join(BASE_DIR, folder)

    # Check if the folder exists
    if not os.path.exists(folder_path):
        flash("Folder does not exist!", "danger")
    elif os.path.isdir(folder_path) and not os.listdir(folder_path):  
        # Delete only if the folder is empty
        os.rmdir(folder_path)
        flash(f"Folder '{folder}' deleted successfully!", "success")
    else:
        flash("Folder is not empty. Delete files first!", "warning")

    return redirect(url_for("Cloud.list_files"))

# Handle file download
@cloud_bp.route("/Download/<path:filename>", methods=["GET"])
def download_file(filename): 
    if "loggedIn" not in session:
        flash("Please log in to access the cloud.", "warning")
        return redirect(url_for("login"))
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

# Handle file deletion

@cloud_bp.route("/delete", methods=["POST"])
def delete_item():   
    if "loggedIn" not in session:
        flash("Please log in to access the cloud.", "warning")
        return redirect(url_for("login"))
    
    form = DeleteForm()
    
    if form.validate_on_submit():
        path = form.path.data
        file_path = os.path.join(BASE_DIR, path)

        # Check if it's a directory or a file
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                # For directories, we use rmtree to delete the entire folder
                shutil.rmtree(file_path)
                flash("Folder deleted successfully", "success")
            else:
                # For files, we use remove
                os.remove(file_path)
                flash("File deleted successfully", "success")
        else:
            flash("File or folder does not exist", "error")
    return redirect(url_for("Cloud.list_files"))