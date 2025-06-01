import os
import pytest
from models import User, Book
from extensions import db

def login(client, username, password):
    """
    Вспомогательная функция: POST /login.
    """
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True
    )

def test_books_access_control(app, client, init_database):
    """
    1) Проверяем, что корневой маршрут "/" доступен всем.
    2) Проверяем, что без логина доступ к "/create" и "/books" (индекс) отдаёт редирект на /login.
       (В коде blueprint для книг использует @login_required.)
    """
    # 1) "/" (главная) свободен — статус 200.
    resp = client.get('/')
    assert resp.status_code == 200

    # 2) "/create" без логина → 302 (редирект на /login)
    resp = client.get('/create', follow_redirects=False)
    assert resp.status_code in (301, 302)

    # 3) "/detail/1" без логина → 302 (попытка войти)
    resp = client.get('/detail/1', follow_redirects=False)
    assert resp.status_code in (301, 302)

def test_book_crud_routes(app, client, init_database):
    """
    Проверяем весь цикл CRUD книг:
    - логинимся как librarian
    - создаём книгу (без файла)
    - убеждаемся, что она видна в списке
    - открываем detail
    - редактируем
    - удаляем
    """
    # Логинимся как librarian1 (из INITIAL_USERS)
    resp = login(client, 'librarian1', 'libpass1')
    assert resp.status_code == 200
    assert b'Вы успешно вошли' in resp.data or b'Успешно' in resp.data

    # 1) Создаём книгу (только поля title, author, year)
    data = {
        'title': 'Route Test Book',
        'author': 'AuthorRT',
        'year': '2021'
    }
    resp = client.post('/create', data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Книга успешно добавлена' in resp.data

    # 2) Проверяем, что книга есть в списке ("/" или "/books" — зависит от регистрации blueprint)
    resp = client.get('/')
    assert b'Route Test Book' in resp.data

    # 3) Получаем ID созданной книги через ORM
    with app.app_context():
        book = Book.query.filter_by(title='Route Test Book').first()
        assert book is not None
        book_id = book.id

    # 4) Заходим на "/detail/<id>"
    resp = client.get(f'/detail/{book_id}')
    assert resp.status_code == 200
    assert b'AuthorRT' in resp.data

    # 5) Редактируем книгу через POST "/edit/<id>"
    edit_data = {
        'title': 'Edited Title',
        'author': 'Edited Author',
        'year': '2022'
    }
    resp = client.post(f'/edit/{book_id}', data=edit_data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Книга успешно обновлена' in resp.data

    # 6) Проверяем, что детали изменились
    resp = client.get(f'/detail/{book_id}')
    assert b'Edited Title' in resp.data
    assert b'Edited Author' in resp.data

    # 7) Удаляем книгу через POST "/delete/<id>"
    resp = client.post(f'/delete/{book_id}', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Книга успешно удалена' in resp.data

    # 8) После удаления detail должен отдавать 404
    resp = client.get(f'/detail/{book_id}', follow_redirects=False)
    assert resp.status_code == 404

def test_book_create_forbidden_for_reader(app, client, init_database):
    """
    Проверяем, что пользователь с ролью 'reader' не может зайти на "/create".
    """
    # Логинимся как reader1 (из INITIAL_USERS)
    resp = login(client, 'reader1', 'readpass1')
    assert resp.status_code == 200

    # GET "/create" → 200 + сообщение «У вас нет прав»
    resp = client.get('/create', follow_redirects=True)
    assert resp.status_code == 200
    assert b'У вас нет прав' in resp.data
