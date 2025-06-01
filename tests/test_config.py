import os
import pytest
from config import Config


def test_roles_mapping():
    # Ensure all expected roles are present
    expected_roles = {'admin', 'librarian', 'reader', 'analyst', 'guest'}
    assert set(Config.ROLES.keys()) >= expected_roles


def test_initial_users_structure():
    # INITIAL_USERS should be a list of dictionaries with required keys
    for user_data in Config.INITIAL_USERS:
        assert 'username' in user_data
        assert 'password' in user_data
        assert 'role' in user_data


def test_upload_folder_path():
    # UPLOAD_FOLDER should be an absolute path ending with 'uploads'
    upload_path = Config.UPLOAD_FOLDER
    assert os.path.isabs(upload_path)
    assert upload_path.endswith(os.path.join('uploads'))
