import db

def add_movie(title, year, recommendation, user_id):
    sql = """INSERT INTO movies (title, year, recommendation, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, year, recommendation, user_id])


def get_movies():
    sql = "SELECT id, title FROM movies ORDER BY id DESC"
    return db.query(sql)


def get_movie(movie_id):
    sql = """SELECT movies.title,
                    movies.year,
                    movies.recommendation,
                    users.username
           FROM movies, users
           WHERE movies.user_id = users.id AND movies.id = ?"""
    return db.query(sql, [movie_id])[0]
