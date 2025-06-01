# tests/conftest.py

import os
import sys
import tempfile
import pytest

# Добавляем в sys.path родительскую папку (ту, где лежат run.py, models.py, и т.д.)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from run import app as flask_app       # теперь import сработает корректно
from extensions import db as _db       # SQLAlchemy-объект из extensions.py
from models import User, Book
from config import Config

@pytest.fixture(scope='session')
def app():
    """
    Создаёт Flask-приложение в режиме TESTING с отдельной SQLite-БД и
    временной папкой для загрузок. При каждом запуске сессии:
      - создаётся временный файл базы
      - создаётся временная директория для UPLOAD_FOLDER
      - инициализируется база и создаются начальные пользователи из Config.INITIAL_USERS
    По окончании сессии база и папка удаляются автоматически.
    """
    # Создаём временный файл для SQLite
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Создаём временную папку для загрузок
    upload_folder = tempfile.mkdtemp()
    flask_app.config['UPLOAD_FOLDER'] = upload_folder

    # Инициализируем базу в контексте приложения
    with flask_app.app_context():
        _db.init_app(flask_app)
        _db.create_all()
        # Создаём «начальных» пользователей из Config.INITIAL_USERS
        for user_data in Config.INITIAL_USERS:
            user = User(
                username=user_data['username'],
                role=user_data['role']
            )
            user.password = user_data['password']
            _db.session.add(user)
        _db.session.commit()

    yield flask_app

    # Teardown: закрываем и удаляем временную БД
    os.close(db_fd)
    os.unlink(db_path)
    # Teardown: удаляем временную папку с загрузками
    try:
        import shutil
        shutil.rmtree(upload_folder)
    except OSError:
        pass

@pytest.fixture(scope='function')
def client(app):
    """
    Возвращает тестовый клиент Flask (app.test_client())
    """
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """
    Возвращает CLI-тестера (app.test_cli_runner())
    """
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def init_database(app):
    """
    Фикстура для очистки БД после каждого теста-функции.
    Таблицы создаются в фикстуре app(); здесь только drop после теста.
    """
    yield
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
