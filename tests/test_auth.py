import pytest
from models import User
from extensions import db

def login(client, username, password):
    """
    Вспомогательная функция: POST /login с данными формы.
    follow_redirects=True, чтобы сразу получить итоговый HTML.
    """
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True
    )

def logout(client):
    """
    GET /logout с follow_redirects=True.
    """
    return client.get('/logout', follow_redirects=True)

def test_register_and_login_logout(app, client, init_database):
    """
    1. Логинимся как admin (из INITIAL_USERS)
    2. Делаем POST /register, создавая нового пользователя reader
    3. Логаутим admin
    4. Логинимся новым пользователем
    5. Логаутим его же
    """
    # 1) Логинимся как admin
    resp = login(client, 'admin', 'adminpass')
    assert resp.status_code == 200
    assert b'Вы успешно вошли' in resp.data or b'Успешно' in resp.data

    # 2) Регистрируем нового пользователя
    resp = client.post(
        '/register',
        data={'username': 'newuser', 'password': 'newpass', 'role': 'reader'},
        follow_redirects=True
    )
    assert resp.status_code == 200
    assert b'Пользователь успешно зарегистрирован' in resp.data

    # 3) Логаутим admin
    resp = logout(client)
    assert resp.status_code == 200
    assert b'Вы вышли' in resp.data

    # 4) Логинимся «newuser»
    resp = login(client, 'newuser', 'newpass')
    assert resp.status_code == 200
    assert b'Вы успешно вошли' in resp.data or b'Успешно' in resp.data

    # 5) Логаутим «newuser»
    resp = logout(client)
    assert resp.status_code == 200
    assert b'Вы вышли' in resp.data

def test_non_admin_cannot_register(app, client, init_database):
    """
    Проверяем, что пользователь с ролью reader не может попасть на /register.
    """
    # Сначала создаём «обычного» пользователя напрямую через ORM
    with app.app_context():
        u = User(username='user2', role='reader')
        u.password = 'pass2'
        db.session.add(u)
        db.session.commit()

    # Логинимся как reader
    resp = login(client, 'user2', 'pass2')
    assert resp.status_code == 200

    # Пытаемся зайти на /register
    resp = client.get('/register', follow_redirects=True)
    assert resp.status_code == 200
    assert b'У вас нет прав' in resp.data
