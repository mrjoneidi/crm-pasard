import os

class Config:
    # Use SQLite for development, but easily switchable to PostgreSQL
    # SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///crm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    UPLOAD_FOLDER = 'uploads'
