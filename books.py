import os
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
    current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Book
from config import Config

books_bp = Blueprint("books", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


@books_bp.route("/")
@login_required
def index():
    books = Book.query.all()
    return render_template("books/index.html", books=books)


@books_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role not in ["admin", "librarian"]:
        flash("У вас нет прав для этой операции", "danger")
        return redirect(url_for("books.index"))

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = int(request.form["year"])

        # Обработка загрузки файла
        file = request.files.get("file")
        file_path = None
        file_name = None

        if file and file.filename != "":
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = Config.UPLOAD_FOLDER
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                file_name = filename
                flash("Файл успешно загружен", "success")
            else:
                flash(
                    "Недопустимый формат файла. Разрешены: pdf, epub, doc, docx, txt",
                    "danger",
                )
                return redirect(url_for("books.create"))

        book = Book(
            title=title,
            author=author,
            year=year,
            added_by=current_user.id,
            file_path=file_path,
            file_name=file_name,
        )
        db.session.add(book)
        db.session.commit()
        flash("Книга успешно добавлена!", "success")
        return redirect(url_for("books.index"))
    return render_template("books/create.html")


@books_bp.route("/detail/<int:id>")
@login_required
def detail(id):
    book = Book.query.get_or_404(id)
    return render_template("books/detail.html", book=book)


@books_bp.route("/download/<int:id>")
@login_required
def download(id):
    book = Book.query.get_or_404(id)
    if not book.file_path or not os.path.exists(book.file_path):
        flash("Файл для этой книги отсутствует", "danger")
        return redirect(url_for("books.detail", id=id))

    directory = os.path.dirname(book.file_path)
    filename = os.path.basename(book.file_path)
    return send_from_directory(
        directory, filename, as_attachment=True, download_name=book.file_name
    )


@books_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    book = Book.query.get_or_404(id)

    # Проверка прав доступа
    if current_user.role not in ["admin", "librarian"]:
        flash("У вас нет прав для редактирования книг", "danger")
        return redirect(url_for("books.index"))

    if request.method == "POST":
        book.title = request.form["title"]
        book.author = request.form["author"]
        book.year = int(request.form["year"])

        # Обработка загрузки нового файла
        file = request.files.get("file")
        if file and file.filename != "":
            if allowed_file(file.filename):
                # Удаляем старый файл
                if book.file_path and os.path.exists(book.file_path):
                    try:
                        os.remove(book.file_path)
                    except Exception as e:
                        current_app.logger.error(f"Ошибка при удалении файла: {str(e)}")

                # Сохраняем новый файл
                filename = secure_filename(file.filename)
                upload_dir = Config.UPLOAD_FOLDER
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

                book.file_path = file_path
                book.file_name = filename
                flash("Файл успешно обновлен", "success")
            else:
                flash("Недопустимый формат файла", "danger")
                return redirect(url_for("books.edit", id=id))

        db.session.commit()
        flash("Книга успешно обновлена", "success")
        return redirect(url_for("books.detail", id=id))

    return render_template("books/edit.html", book=book)


@books_bp.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    book = Book.query.get_or_404(id)

    # Проверка прав доступа
    if current_user.role not in ["admin", "librarian"]:
        flash("У вас нет прав для удаления книг", "danger")
        return redirect(url_for("books.index"))

    if request.method == "POST":
        # Удаляем файл книги, если он существует
        if book.file_path and os.path.exists(book.file_path):
            try:
                os.remove(book.file_path)
            except Exception as e:
                current_app.logger.error(f"Ошибка при удалении файла: {str(e)}")

        # Удаляем книгу из базы данных
        db.session.delete(book)
        db.session.commit()

        flash("Книга успешно удалена", "success")
        return redirect(url_for("books.index"))

    return render_template("books/delete.html", book=book)
