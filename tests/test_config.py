from config import Config
import os
import pytest

def test_upload_folder_setting(app):

    uf = app.config['UPLOAD_FOLDER']
    assert os.path.isdir(uf), f"UPLOAD_FOLDER '{uf}' no dir"

def test_roles_definition():

    expected_roles = {'admin', 'librarian', 'reader', 'analyst', 'guest'}
    assert set(Config.ROLES.keys()) == expected_roles, (
        f"В Config.ROLES  {expected_roles}, "
        f"found {set(Config.ROLES.keys())}"
    )
