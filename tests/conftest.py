# tests/conftest.py

import os
import sys
import tempfile
import pytest


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from run import app as flask_app       
from extensions import db as _db      
from models import User, Book
from config import Config

@pytest.fixture(scope='session')
def app():


    db_fd, db_path = tempfile.mkstemp()
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    upload_folder = tempfile.mkdtemp()
    flask_app.config['UPLOAD_FOLDER'] = upload_folder


    with flask_app.app_context():
        _db.init_app(flask_app)
        _db.create_all()

        for user_data in Config.INITIAL_USERS:
            user = User(
                username=user_data['username'],
                role=user_data['role']
            )
            user.password = user_data['password']
            _db.session.add(user)
        _db.session.commit()

    yield flask_app


    os.close(db_fd)
    os.unlink(db_path)

    try:
        import shutil
        shutil.rmtree(upload_folder)
    except OSError:
        pass

@pytest.fixture(scope='function')
def client(app):

    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):

    return app.test_cli_runner()

@pytest.fixture(scope='function')
def init_database(app):

    yield
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
