import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key_here"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "library.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True
    MAX_CONTENT_LENGTH = int(
        os.environ.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    )  # 10 MB
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "epub", "doc", "docx", "txt"}

    ROLES = {
        "admin": ["create", "read", "update", "delete", "manage_users"],
        "librarian": ["create", "read", "update", "delete"],
        "reader": ["read"],
        "analyst": ["read", "export"],
        "guest": [],
    }

    INITIAL_USERS = [
        {"username": "admin", "password": "adminpass", "role": "admin"},
        {"username": "librarian1", "password": "libpass1", "role": "librari"},
        {"username": "reader1", "password": "readpass1", "role": "reader"},
        {"username": "analyst1", "password": "anpass1", "role": "analyst"},
        {"username": "guest", "password": "guestpass", "role": "guest"},
    ]
