import os
import pytest
from models import User, Book
from extensions import db

def login(client, username, password):
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True
    )

def test_books_access_control(app, client, init_database):


    resp = client.get('/')
    assert resp.status_code == 200


    resp = client.get('/create', follow_redirects=False)
    assert resp.status_code in (301, 302)


    resp = client.get('/detail/1', follow_redirects=False)
    assert resp.status_code in (301, 302)

def test_book_crud_routes(app, client, init_database):


    resp = login(client, 'librarian1', 'libpass1')
    assert resp.status_code == 200
    assert b'enter' in resp.data or b'done' in resp.data


    data = {
        'title': 'Route Test Book',
        'author': 'AuthorRT',
        'year': '2021'
    }
    resp = client.post('/create', data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'book added' in resp.data


    resp = client.get('/')
    assert b'Route Test Book' in resp.data


    with app.app_context():
        book = Book.query.filter_by(title='Route Test Book').first()
        assert book is not None
        book_id = book.id

    resp = client.get(f'/detail/{book_id}')
    assert resp.status_code == 200
    assert b'AuthorRT' in resp.data


    edit_data = {
        'title': 'Edited Title',
        'author': 'Edited Author',
        'year': '2022'
    }
    resp = client.post(f'/edit/{book_id}', data=edit_data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'done' in resp.data


    resp = client.get(f'/detail/{book_id}')
    assert b'Edited Title' in resp.data
    assert b'Edited Author' in resp.data


    resp = client.post(f'/delete/{book_id}', follow_redirects=True)
    assert resp.status_code == 200
    assert b'deleted' in resp.data


    resp = client.get(f'/detail/{book_id}', follow_redirects=False)
    assert resp.status_code == 404

def test_book_create_forbidden_for_reader(app, client, init_database):


    resp = login(client, 'reader1', 'readpass1')
    assert resp.status_code == 200


    resp = client.get('/create', follow_redirects=True)
    assert resp.status_code == 200
    assert b'NO' in resp.data
