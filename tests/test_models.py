import pytest
from models import User, Book
from extensions import db

def test_user_password_hashing(app, init_database):
    """
    Проверяем, что при установке пароля он хэштируется,
    а метод verify_password корректно проверяет и валидный, и
    невалидный пароль.
    """
    with app.app_context():
        u = User(username='testuser', role='reader')
        u.password = 'mypassword'
        db.session.add(u)
        db.session.commit()

        fetched = User.query.filter_by(username='testuser').first()
        assert fetched is not None, "Пользователь не был сохранён в БД"
        assert fetched.verify_password('mypassword'), "Верный пароль не прошёл проверку"
        assert not fetched.verify_password('wrongpassword'), "Неверный пароль ошибочно проходит проверку"

def test_book_model_crud(app, init_database):
    """
    Проверяем операции CRUD для модели Book:
    - создание книги с ссылки на пользователя
    - чтение
    - обновление
    - удаление
    """
    with app.app_context():
        # Находим заранее созданного admin-пользователя
        user = User.query.filter_by(username='admin').first()
        assert user is not None, "Админ-пользователь из INITIAL_USERS не создан"

        # Создаём книгу
        book = Book(
            title='Test Book',
            author='Author',
            year=2020,
            added_by=user.id
        )
        db.session.add(book)
        db.session.commit()

        # Читаем эту книгу
        fetched = Book.query.filter_by(title='Test Book').first()
        assert fetched is not None, "Книга не найдена после создания"
        assert fetched.author == 'Author'
        assert fetched.year == 2020
        assert fetched.added_by == user.id

        # Обновляем книгу
        fetched.title = 'Updated Title'
        db.session.commit()
        updated = Book.query.get(fetched.id)
        assert updated.title == 'Updated Title', "Название книги не обновилось"

        # Удаляем книгу
        db.session.delete(updated)
        db.session.commit()
        deleted = Book.query.get(fetched.id)
        assert deleted is None, "Книга не удалена"
