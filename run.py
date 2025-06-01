import os
from flask import Flask, render_template
from extensions import db, login_manager
from config import Config

# Регистрация Blueprint'ов
from auth import auth_bp
from books import books_bp
from main import main_bp

#secret = "123123"

app = Flask(__name__)
app.config.from_object(Config)

# Явная установка URI базы данных
if "DATABASE_URL" in app.config:
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"]

# Инициализация расширений
db.init_app(app)
login_manager.init_app(app)

# Создаем папку для загрузок, если ее нет
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(main_bp)

login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    from models import User

    return User.query.get(int(user_id))


@app.errorhandler(403)
def forbidden_error(error):
    return render_template("errors/403.html"), 403


# Инициализация БД при запуске
with app.app_context():
    db.create_all()

    # Создание начальных пользователей
    from config import Config
    from models import User

    for user_data in Config.INITIAL_USERS:
        user = User.query.filter_by(username=user_data["username"]).first()
        if not user:
            user = User(username=user_data["username"], role=user_data["role"])
            user.password = user_data["password"]
            db.session.add(user)

    db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
