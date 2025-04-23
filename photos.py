import db

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


def remove_poster(movie_id, poster_id):
    sql = "DELETE FROM posters WHERE id = ? AND movie_id = ?"
    db.execute(sql, [poster_id, movie_id])


def remove_image(movie_id, image_id):
    sql = "DELETE FROM images WHERE id = ? AND movie_id = ?"
    db.execute(sql, [image_id, movie_id])


