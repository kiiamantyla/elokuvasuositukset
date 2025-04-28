from werkzeug.security import generate_password_hash, check_password_hash

import db
import movies

def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_movies(user_id):
    sql = """SELECT movies.id,
                    movies.title,
                    movies.year,
                    movies.grade,
                    movies.user_id,
                    COUNT(reviews.id) review_count
             FROM movies
             LEFT JOIN reviews ON reviews.movie_id = movies.id
             WHERE movies.user_id = ?
             GROUP BY movies.id
             ORDER BY movies.id DESC"""
    results = [dict(row) for row in db.query(sql, [user_id])]

    for movie in results:
        classes = movies.get_movie_classes(movie["id"])
        movie["genres"] = [c for c in classes if c["title"] == "genre"]
        age = next((c["value"] for c in classes if c["title"] == "ikäraja"), None)
        movie["age_limit"] = age

    return results


def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])


def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    return None
