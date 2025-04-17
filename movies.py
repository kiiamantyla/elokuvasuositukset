import db

def add_movie(title, year, grade, recommendation, user_id, classes):
    sql = """INSERT INTO movies (title, year, grade, recommendation, user_id)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, year, grade, recommendation, user_id])

    movie_id = db.last_insert_id()
    sql = "INSERT INTO movie_classes (movie_id, class_id) VALUES (?, ?)"
    for class_title, class_value in classes:
        class_id = get_class_id(class_title, class_value)
        if class_id:
            db.execute(sql, [movie_id, class_id])
    return movie_id


def add_image(movie_id, image):
    sql = "INSERT INTO images (movie_id, image) VALUES (?, ?)"
    db.execute(sql, [movie_id, image])


def add_poster(movie_id, poster):
    sql = "INSERT INTO posters (movie_id, poster) VALUES (?, ?)"
    db.execute(sql, [movie_id, poster])


def get_images(movie_id):
    sql = "SELECT id FROM images WHERE movie_id = ?"
    return db.query(sql, [movie_id])


def get_posters(movie_id):
    sql = "SELECT id FROM posters WHERE movie_id = ?"
    return db.query(sql, [movie_id])


def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None


def get_poster(poster_id):
    sql = "SELECT poster FROM posters WHERE id = ?"
    result = db.query(sql, [poster_id])
    return result[0][0] if result else None


def add_review(movie_id, user_id, grade, review):
    sql = """INSERT INTO reviews (movie_id, user_id, grade, review)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [movie_id, user_id, grade, review])


def get_reviews(movie_id):
    sql = """SELECT reviews.review,
                    reviews.grade,
                    reviews.user_id,
                    users.username
             FROM reviews, users
             WHERE reviews.movie_id = ? AND reviews.user_id = users.id
             ORDER BY reviews.id DESC"""
    return db.query(sql, [movie_id])


def get_class_id(title, value):
    sql = "SELECT id FROM classes WHERE title = ? AND value = ?"
    result = db.query(sql, [title, value])
    return result[0]["id"] if result else None


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        if title not in classes:
            classes[title] = []
        classes[title].append(value)
    return classes


def get_movie_classes(movie_id):
    sql = """SELECT classes.title, classes.value
             FROM movie_classes
             JOIN classes ON movie_classes.class_id = classes.id
             WHERE movie_classes.movie_id = ?"""
    return db.query(sql, [movie_id])


def get_movies():
    sql = "SELECT id, title FROM movies ORDER BY id DESC"
    return db.query(sql)


def get_movie(movie_id):
    sql = """SELECT movies.id,
                    movies.title,
                    movies.year,
                    movies.grade,
                    movies.recommendation,
                    users.id user_id,
                    users.username
           FROM movies, users
           WHERE movies.user_id = users.id AND movies.id = ?"""
    result = db.query(sql, [movie_id])
    return result[0] if result else None


def update_movie(movie_id, title, year, grade, recommendation, classes):
    sql = """UPDATE movies SET title = ?,
                               year = ?,
                               grade = ?,
                               recommendation = ?
                           WHERE id = ?"""
    db.execute(sql, [title, year, grade, recommendation, movie_id])

    sql = "DELETE FROM movie_classes WHERE movie_id = ?"
    db.execute(sql, [movie_id])

    sql = "INSERT INTO movie_classes (movie_id, class_id) VALUES (?, ?)"
    for class_title, class_value in classes:
        class_id = get_class_id(class_title, class_value)
        if class_id:
            db.execute(sql, [movie_id, class_id])


def remove_movie(movie_id):
    sql = "DELETE FROM movie_classes WHERE movie_id = ?"
    db.execute(sql, [movie_id])
    sql = "DELETE FROM movies WHERE id = ?"
    db.execute(sql, [movie_id])


def find_movies(query):
    sql = """SELECT id, title
             FROM movies
             WHERE title LIKE ? OR year LIKE ? OR recommendation LIKE ?
             ORDER BY id DESC"""
    params = ["%" + query + "%", "%" + query + "%", "%" + query + "%"]
    return db.query(sql, params)
