from werkzeug.security import generate_password_hash, check_password_hash

import db
import movies

def get_user(user_id):
    sql = """SELECT id,
                    username,
                    profile_picture,
                    profile_picture IS NOT NULL has_profile_picture
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_movies(user_id, page, page_size):
    limit = page_size
    offset = page_size * (page - 1)

    sql = """SELECT movies.id,
                    movies.title,
                    movies.year,
                    movies.user_id,
                    COUNT(reviews.id) AS review_count
             FROM movies
             LEFT JOIN reviews ON reviews.movie_id = movies.id
             WHERE movies.user_id = ?
             GROUP BY movies.id
             ORDER BY movies.id DESC
             LIMIT ? OFFSET ?"""

    results = db.query(sql, [user_id, limit, offset])
    results = [dict(row) for row in results]

    for movie in results:
        classes = movies.get_movie_classes(movie["id"])
        movie["genres"] = [c for c in classes if c["title"] == "genre"]
        age = next((c["value"] for c in classes if c["title"] == "ikäraja"), None)
        movie["age_limit"] = age

    return results


def movie_count(user_id):
    sql = "SELECT COUNT(*) AS count FROM movies WHERE user_id = ?"
    result = db.query(sql, [user_id])
    return result[0]["count"] if result else 0


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


def update_image(user_id, profile_picture):
    sql = "UPDATE users SET profile_picture = ? WHERE id = ?"
    db.execute(sql, [profile_picture, user_id])


def get_profile_picture(user_id):
    sql = "SELECT profile_picture FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None


def remove_profile_picture(user_id):
    sql = "UPDATE users SET profile_picture = NULL WHERE id = ?"
    db.execute(sql, [user_id])
