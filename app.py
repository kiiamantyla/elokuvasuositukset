import sqlite3
import re
import secrets
import markupsafe

from flask import Flask
from flask import abort, flash, make_response, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash

import config
import db
import movies
import users
import photos



app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


def check_csrf():
    if "csrf_token" not in request.form:
        abprt(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


@app.route("/")
def index():
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)


@app.route("/images/<int:movie_id>")
def edit_images(movie_id):
    require_login()

    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    images = photos.get_images(movie_id)
    posters = photos.get_posters(movie_id)

    return render_template("images.html", movie=movie, images=images, posters=posters)


@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()

    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    poster = request.files["poster"]
    if poster:
        if not poster.filename.endswith(".jpg"):
            flash("VIRHE: väärä tiedostomuoto")
            return redirect("/images/" + str(movie_id))

        image = poster.read()
        if len(image) > 100 * 1024:
            flash("VIRHE: liian suuri kuva")
            return redirect("/images/" + str(movie_id))

        photos.add_poster(movie_id, image)


    image_file = request.files["image"]
    if image_file:
        if not image_file.filename.endswith(".jpg"):
            flash("VIRHE: väärä tiedostomuoto")
            return redirect("/images/" + str(movie_id))

        image = image_file.read()
        if len(image) > 100 * 1024:
            flash("VIRHE: liian suuri kuva")
            return redirect("/images/" + str(movie_id))

        photos.add_image(movie_id, image)

    return redirect("/movie/" + str(movie_id))


@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()
    check_csrf()

    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)


    for poster_id in request.form.getlist("poster_id"):
        photos.remove_poster(movie_id, poster_id)

    for image_id in request.form.getlist("image_id"):
        photos.remove_image(movie_id, image_id)

    return redirect("/images/" + str(movie_id))


@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = photos.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/poster/<int:poster_id>")
def show_poster(poster_id):
    poster = photos.get_poster(poster_id)
    if not poster:
        abort(404)

    response = make_response(bytes(poster))
    response.headers.set("Content-Type", "poster/jpeg")
    return response


@app.route("/create_review", methods=["POST"])
def create_review():
    require_login()
    check_csrf()

    grade = request.form["grade"]
    if not re.search("^[1-9]$|^10$", grade):
        abort(403)
    review = request.form["review"]
    if not review or len(review) > 1000:
        abort(403)

    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(403)

    user_id = session["user_id"]

    movies.add_review(movie_id, user_id, grade, review)
    return redirect("/movie/" + str(movie_id))


@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    movies = users.get_movies(user_id)
    return render_template("show_user.html", user=user, movies=movies)


@app.route("/find_movie")
def find_movie():
    query = request.args.get("query")
    if query:
        results = movies.find_movies(query)
    else:
        query = ""
        results = []
    return render_template("find_movie.html", query=query, results=results)


@app.route("/movie/<int:movie_id>")
def show_movie(movie_id):
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    classes = movies.get_movie_classes(movie_id)
    genres = []
    age_limit = None

    for class_item in classes:
        if class_item["title"] == "genre":
            genres.append(class_item)
        elif class_item["title"] == "ikäraja":
            age_limit = class_item

    all_classes = movies.get_all_classes()
    reviews = movies.get_reviews(movie_id)
    images = photos.get_images(movie_id)
    posters = photos.get_posters(movie_id)

    return render_template("show_movie.html", movie=movie, genres=genres, age_limit=age_limit, all_classes=all_classes, reviews=reviews, images=images, posters=posters)


@app.route("/new_movie")
def new_movie():
    require_login()
    classes = movies.get_all_classes()
    genres = classes.get("genre", [])
    age_limits = classes.get("ikäraja", [])
    return render_template("new_movie.html", genres=genres, age_limits=age_limits)


@app.route("/create_movie", methods=["POST"])
def create_movie():
    require_login()
    check_csrf()

    title = request.form["title"]
    if not title or len(title) > 90:
        abort(403)
    year = request.form["year"]
    if not re.search("^[1-9][0-9]{0,3}$", year):
        abort(403)
    grade = request.form["grade"]
    if not re.search("^[1-9]$|^10$", grade):
        abort(403)
    recommendation = request.form["recommendation"]
    if not recommendation or len(recommendation) > 500:
        abort(403)
    user_id = session["user_id"]

    all_classes = movies.get_all_classes()
    selected_classes = []

    selected_genres = request.form.getlist("genres")

    if "" in selected_genres and len(selected_genres) > 1:
        abort(403)

    for genre in selected_genres:
        if genre:
            try:
                class_title, class_value = genre.split(":")
            except ValueError:
                abort(403)
            class_title, class_value = genre.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            if class_title == "genre" and class_value in all_classes["genre"]:
                selected_classes.append((class_title, class_value))

    age_limit = request.form.get("age_limit")
    if age_limit:
        try:
            class_title, class_value = age_limit.split(":")
        except ValueError:
            abort(403)
        if class_title not in all_classes:
            abort(403)
        if class_value not in all_classes[class_title]:
            abort(403)
        if class_title == "ikäraja" and class_value in all_classes["ikäraja"]:
            selected_classes.append((class_title, class_value))

    movie_id = movies.add_movie(title, year, grade, recommendation, user_id, selected_classes)

    return redirect("/movie/" + str(movie_id))


@app.route("/edit_movie/<int:movie_id>")
def edit_movie(movie_id):
    require_login()

    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    classes = movies.get_movie_classes(movie_id)
    all_classes = movies.get_all_classes()

    genres = [class_item["value"] for class_item in classes if class_item["title"] == "genre"]
    age_limits = [class_item["value"] for class_item in classes if class_item["title"] == "ikäraja"]

    all_genres = all_classes.get("genre", [])
    all_age_limits = all_classes.get("ikäraja", [])
    return render_template("edit_movie.html", movie=movie, genres=genres, age_limits=age_limits, all_genres=all_genres, all_age_limits=all_age_limits)


@app.route("/update_movie", methods=["POST"])
def update_movie():
    require_login()
    check_csrf()

    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 90:
        abort(403)
    year = request.form["year"]
    if not re.search("^[1-9][0-9]{0,3}$", year):
        abort(403)
    grade = request.form["grade"]
    if not re.search("^[1-9]$|^10$", grade):
        abort(403)
    recommendation = request.form["recommendation"]
    if not recommendation or len(recommendation) > 1000:
        abort(403)

    all_classes = movies.get_all_classes()
    selected_classes = []

    selected_genres = request.form.getlist("genres")

    if "" in selected_genres and len(selected_genres) > 1:
        abort(403)

    for genre in selected_genres:
        if genre:
            try:
                class_title, class_value = genre.split(":")
            except ValueError:
                abort(403)
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            if class_title == "genre" and class_value in all_classes["genre"]:
                selected_classes.append((class_title, class_value))

    age_limit = request.form.get("age_limit")
    if age_limit:
        try:
            class_title, class_value = age_limit.split(":")
        except ValueError:
            abort(403)
        if class_title not in all_classes:
            abort(403)
        if class_value not in all_classes[class_title]:
            abort(403)
        if class_title == "ikäraja" and class_value in all_classes["ikäraja"]:
            selected_classes.append((class_title, class_value))

    movies.update_movie(movie_id, title, year, grade, recommendation, selected_classes)
    return redirect("/movie/" + str(movie_id))


@app.route("/remove_movie/<int:movie_id>", methods=["GET", "POST"])
def remove_movie(movie_id):
    require_login()

    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_movie.html", movie=movie)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            movies.remove_movie(movie_id)
            return redirect("/")
        else:
            return redirect("/movie/" + str(movie_id))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or not password1 or not password2:
        abort(403)

    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return redirect("/register")
    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")

    flash("Tunnus luotu")
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("VIRHE: väärä tunnus tai salasana")
            return redirect("/login")



@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
