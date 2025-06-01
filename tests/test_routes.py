import pytest
from run import app as flask_app

@pytest.fixture
def client():

    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

    assert b'<html' in response.data or b'<!DOCTYPE' in response.data


def test_login_page_loads(client):
    response = client.get('/login')

    assert response.status_code == 200
    assert b'<form' in response.data


def test_nonexistent_route(client):
    response = client.get('/nonexistent')
    assert response.status_code in (404,)
