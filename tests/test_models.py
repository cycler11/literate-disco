import pytest
from models import User, Book
from extensions import db

def test_user_password_hashing(app, init_database):

    with app.app_context():
        u = User(username='testuser', role='reader')
        u.password = 'mypassword'
        db.session.add(u)
        db.session.commit()

        fetched = User.query.filter_by(username='testuser').first()
        assert fetched is not None, "No saved user"
        assert fetched.verify_password('mypassword'), "wrong pass"
        assert not fetched.verify_password('wrongpassword'), "whhwhw"

def test_book_model_crud(app, init_database):

    with app.app_context():

        user = User.query.filter_by(username='admin').first()
        assert user is not None, "admin is not created"


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
        assert fetched is not None, "no book was found"
        assert fetched.author == 'Author'
        assert fetched.year == 2020
        assert fetched.added_by == user.id

        # Обновляем книгу
        fetched.title = 'Updated Title'
        db.session.commit()
        updated = Book.query.get(fetched.id)
        assert updated.title == 'Updated Title', "no name"

        # Удаляем книгу
        db.session.delete(updated)
        db.session.commit()
        deleted = Book.query.get(fetched.id)
        assert deleted is None, "no delete"
