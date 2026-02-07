import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def generate_unique_filename(filename):
    """Generates a unique filename using UUID."""
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    return unique_name

def save_file(file_storage):
    """Saves a file to the configured upload folder and returns the relative path."""
    if not file_storage:
        return None

    filename = secure_filename(file_storage.filename)
    unique_filename = generate_unique_filename(filename)

    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = os.path.join(upload_folder, unique_filename)
    file_storage.save(file_path)

    return unique_filename
