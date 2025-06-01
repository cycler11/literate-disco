import pytest
from flask import Flask
from extensions import db
from models import User, Book

@pytest.fixture
def app():
    # Create a Flask app configured for testing
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_user_password(app):
    # Test that setting a password hashes correctly and verify_password works
    user = User(username='testuser', role='reader')
    user.password = 'secret'
    assert user.verify_password('secret')
    assert not user.verify_password('wrong')


def test_book_model_crud(app):
    # Test basic CRUD operations for Book model
    book = Book(title='Test Title', author='Author Name', year=2021,
                added_by=1, file_path='path/to/file.pdf', file_name='file.pdf')
    db.session.add(book)
    db.session.commit()
    # There should be exactly one book in the database
    assert Book.query.count() == 1
    retrieved = Book.query.first()
    assert retrieved.title == 'Test Title'
    # Test update
    retrieved.title = 'New Title'
    db.session.commit()
    updated = Book.query.first()
    assert updated.title == 'New Title'
    # Test delete
    db.session.delete(updated)
    db.session.commit()
    assert Book.query.count() == 0
