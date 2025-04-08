import db

def add_movie(title, year, recommendation, user_id, classes):
    sql = """INSERT INTO movies (title, year, recommendation, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, year, recommendation, user_id])

    movie_id = db.last_insert_id()

    sql = "INSERT INTO movie_classes (movie_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [movie_id, title, value])


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        if title not in classes:
            classes[title] = []
        classes[title].append(value)
    return classes


def get_classes(movie_id):
    sql = "SELECT title, value FROM movie_classes WHERE movie_id = ?"
    return db.query(sql, [movie_id])


def get_movies():
    sql = "SELECT id, title FROM movies ORDER BY id DESC"
    return db.query(sql)


def get_movie(movie_id):
    sql = """SELECT movies.id,
                    movies.title,
                    movies.year,
                    movies.recommendation,
                    users.id user_id,
                    users.username
           FROM movies, users
           WHERE movies.user_id = users.id AND movies.id = ?"""
    result = db.query(sql, [movie_id])
    return result[0] if result else None


def update_movie(movie_id, title, year, recommendation, classes):
    sql = """UPDATE movies SET title = ?,
                               year = ?,
                               recommendation = ?
                           WHERE id = ?"""
    db.execute(sql, [title, year, recommendation, movie_id])

    sql = "DELETE FROM movie_classes WHERE movie_id = ?"
    db.execute(sql, [movie_id])

    sql = "INSERT INTO movie_classes (movie_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [movie_id, title, value])


def remove_movie(movie_id):
    sql = "DELETE FROM movies WHERE id = ?"
    db.execute(sql, [movie_id])


def find_movies(query):
    sql = """SELECT id, title
             FROM movies
             WHERE title LIKE ? OR year LIKE ? OR recommendation LIKE ?
             ORDER BY id DESC"""
    params = ["%" + query + "%", "%" + query + "%", "%" + query + "%"]
    return db.query(sql, params)
