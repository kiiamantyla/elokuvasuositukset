import sqlite3
import re

from flask import Flask
from flask import abort, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash

import config
import db
import movies
import users



app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


@app.route("/")
def index():
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)


@app.route("/create_review", methods=["POST"])
def create_review():
    require_login()

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
    items = users.get_items(user_id)
    return render_template("show_user.html", user=user, items=items)


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
    classes = movies.get_classes(movie_id)
    reviews = movies.get_reviews(movie_id)
    return render_template("show_movie.html",movie=movie, classes=classes, reviews=reviews)


@app.route("/new_movie")
def new_movie():
    require_login()
    classes = movies.get_all_classes()
    return render_template("new_movie.html", classes=classes)


@app.route("/create_movie", methods=["POST"])
def create_movie():
    require_login()

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

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            entry_title, entry_value = entry.split(":")
            if entry_title not in all_classes:
                abort(403)
            if entry_value not in all_classes[entry_title]:
                abort(403)
            classes.append((entry_title, entry_value))

    movies.add_movie(title, year, grade, recommendation, user_id, classes)
    return redirect("/")


@app.route("/edit_movie/<int:movie_id>")
def edit_movie(movie_id):
    require_login()

    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    all_classes = movies.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in movies.get_classes(movie_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_movie.html", movie=movie, classes=classes,  all_classes=all_classes)


@app.route("/update_movie", methods=["POST"])
def update_movie():
    require_login()

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
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            entry_title, entry_value = entry.split(":")
            if entry_title not in all_classes:
                abort(403)
            if entry_value not in all_classes[entry_title]:
                abort(403)
            classes.append((entry_title, entry_value))

    movies.update_movie(movie_id, title, year, grade, recommendation, classes)
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
        return "VIRHE: salasanat eivät ole samat"

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"


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
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
