import pytest
from models import User
from extensions import db

def login(client, username, password):
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True
    )

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_register_and_login_logout(app, client, init_database):


    resp = login(client, 'admin', 'adminpass')
    assert resp.status_code == 200
    assert b'enter done' in resp.data or b'succeeesss' in resp.data


    resp = client.post(
        '/register',
        data={'username': 'newuser', 'password': 'newpass', 'role': 'reader'},
        follow_redirects=True
    )
    assert resp.status_code == 200
    assert b'registered' in resp.data


    resp = logout(client)
    assert resp.status_code == 200
    assert b'exit' in resp.data


    resp = login(client, 'newuser', 'newpass')
    assert resp.status_code == 200
    assert b'enter' in resp.data or b'done' in resp.data


    resp = logout(client)
    assert resp.status_code == 200
    assert b'exit_done' in resp.data

def test_non_admin_cannot_register(app, client, init_database):

    with app.app_context():
        u = User(username='user2', role='reader')
        u.password = 'pass2'
        db.session.add(u)
        db.session.commit()


    resp = login(client, 'user2', 'pass2')
    assert resp.status_code == 200


    resp = client.get('/register', follow_redirects=True)
    assert resp.status_code == 200
    assert b'NO' in resp.data
