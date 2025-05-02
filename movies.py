import db

def add_movie(movie_details, user_id, classes):
    title = movie_details["title"]
    year = movie_details["year"]
    grade = movie_details["grade"]
    recommendation = movie_details["recommendation"]

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
    sql = """SELECT movies.id,
                    movies.title,
                    movies.user_id,
                    users.id,
                    users.username,
                    COUNT(reviews.id) review_count
             FROM movies JOIN users ON movies.user_id = users.id
                         LEFT JOIN reviews ON movies.id = reviews.movie_id
             GROUP BY movies.id
             ORDER BY movies.id DESC"""
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


def update_movie(movie_id, movie_details, classes):
    title = movie_details["title"]
    year = movie_details["year"]
    grade = movie_details["grade"]
    recommendation = movie_details["recommendation"]

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
    sql = "DELETE FROM images WHERE movie_id = ?"
    db.execute(sql, [movie_id])
    sql = "DELETE FROM posters WHERE movie_id = ?"
    db.execute(sql, [movie_id])
    sql = "DELETE FROM reviews WHERE movie_id = ?"
    db.execute(sql, [movie_id])
    sql = "DELETE FROM movies WHERE id = ?"
    db.execute(sql, [movie_id])


def find_movies(search_params):

    query = search_params["query"]
    min_grade = search_params["min_grade"]
    min_year = search_params["min_year"]
    max_year = search_params["max_year"]
    username = search_params["username"]
    genres = search_params["genres"]
    age_limits = search_params["age_limits"]


    sql ="""SELECT DISTINCT movies.id, movies.title
             FROM movies
             LEFT JOIN movie_classes mc_genre ON movies.id = mc_genre.movie_id
             LEFT JOIN classes c_genre ON
                       mc_genre.class_id = c_genre.id AND
                       c_genre.title = 'genre'
             LEFT JOIN movie_classes mc_age ON movies.id = mc_age.movie_id
             LEFT JOIN classes c_age ON
                       mc_age.class_id = c_age.id AND
                       c_age.title = 'ikäraja'
             LEFT JOIN users ON movies.user_id = users.id
             LEFT JOIN reviews ON movies.id = reviews.movie_id
             WHERE 1=1"""

    params = []

    if query:
        sql += """ AND (
                movies.title LIKE ?
                OR movies.recommendation LIKE ?
                OR reviews.review LIKE ?
                )"""
        pattern = "%" + query + "%"
        params += [pattern] * 3

    if min_year:
        sql += " AND movies.year >= ?"
        params.append(min_year)

    if max_year:
        sql += " AND movies.year <= ?"
        params.append(max_year)

    if min_grade:
        sql += " AND movies.grade >= ?"
        params.append(min_grade)

    if username:
        sql += " AND users.username LIKE ?"
        params.append("%" + username + "%")

    if genres:
        genre_list = [
            genre.split(":")[1] if genre.startswith("genre:") else genre
            for genre in genres.split(",")
        ]
        placeholders = ",".join("?" * len(genre_list))
        sql += f" AND c_genre.value IN ({placeholders})"
        params.extend(genre_list)

    if age_limits:
        age_limit_list = [
            age_limit.split(":")[1] if age_limit.startswith("ikäraja:") else age_limit
            for age_limit in age_limits.split(",")
        ]
        placeholders = ",".join("?" * len(age_limit_list))
        sql += f" AND c_age.value IN ({placeholders})"
        params.extend(age_limit_list)

    sql += " ORDER BY movies.id DESC"

    return db.query(sql, params)
