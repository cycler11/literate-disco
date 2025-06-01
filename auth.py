from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from config import Config

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user)
            next_page = request.args.get("next")
            flash("Вы успешно вошли в систему!", "success")
            return redirect(next_page or url_for("main.index"))
        flash("Неверное имя пользователя или пароль", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if current_user.role != "admin":
        flash("У вас нет прав для этой операции", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        # Запрет на создание новых администраторов
        if role == "admin":
            flash("Создание новых администраторов запрещено", "danger")
            roles = [r for r in Config.ROLES.keys() if r != "admin"]
            return render_template("auth/register.html", roles=roles)

        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким именем уже существует", "danger")
        else:
            user = User(username=username, role=role)
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash("Пользователь успешно зарегистрирован!", "success")
            return redirect(url_for("main.index"))

    # Убираем роль администратора из доступных для выбора
    roles = [role for role in Config.ROLES.keys() if role != "admin"]
    return render_template("auth/register.html", roles=roles)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("auth.login"))
