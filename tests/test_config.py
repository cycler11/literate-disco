from config import Config
import os
import pytest

def test_upload_folder_setting(app):
    """
    Проверяет, что в app.config задана временная папка UPLOAD_FOLDER
    и она реально существует (как директория).
    """
    uf = app.config['UPLOAD_FOLDER']
    assert os.path.isdir(uf), f"UPLOAD_FOLDER '{uf}' не является директорией"

def test_roles_definition():
    """
    Проверяем, что в Config.ROLES определены ровно эти роли:
    admin, librarian, reader, analyst, guest.
    """
    expected_roles = {'admin', 'librarian', 'reader', 'analyst', 'guest'}
    assert set(Config.ROLES.keys()) == expected_roles, (
        f"В Config.ROLES ожидались роли {expected_roles}, "
        f"нашли {set(Config.ROLES.keys())}"
    )
