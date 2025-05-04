import db


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


def get_review_stats(movie_id):
    sql = """SELECT COUNT(*) count,
                    ROUND(AVG(grade), 1) average
             FROM reviews
             WHERE movie_id = ?"""
    result = db.query(sql, [movie_id])
    return result[0] if result else {"count": 0, "average": None}


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


def get_movies(page=None, page_size=None):
    sql = """SELECT movies.id,
                    movies.title,
                    movies.user_id,
                    users.id,
                    users.username,
                    COUNT(reviews.id) review_count
             FROM movies JOIN users ON movies.user_id = users.id
                         LEFT JOIN reviews ON movies.id = reviews.movie_id
             GROUP BY movies.id
             ORDER BY movies.id DESC
             LIMIT ? OFFSET ?"""

    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])


def movie_count():
    sql = "SELECT COUNT(*) count FROM movies"
    result = db.query(sql)
    return result[0]["count"] if result else 0


def get_movie(movie_id):
    sql = """SELECT movies.id,
                    movies.title,
                    movies.year,
                    movies.duration,
                    movies.director,
                    movies.language,
                    movies.main_actors,
                    movies.imdb_url,
                    users.id user_id,
                    users.username
           FROM movies, users
           WHERE movies.user_id = users.id AND movies.id = ?"""
    result = db.query(sql, [movie_id])
    return result[0] if result else None


def add_movie(movie_details, user_id, classes):
    title = movie_details["title"]
    year = movie_details["year"]
    duration = movie_details["duration"]
    director = movie_details["director"]
    language = movie_details["language"]
    main_actors = movie_details["main_actors"]
    imdb_url = movie_details["imdb_url"]

    sql = """INSERT INTO movies (title,
                                 year,
                                 duration,
                                 director,
                                 language,
                                 main_actors,
                                 imdb_url,
                                 user_id)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, year, duration, director,
                     language, main_actors, imdb_url, user_id])

    movie_id = db.last_insert_id()
    sql = "INSERT INTO movie_classes (movie_id, class_id) VALUES (?, ?)"
    for class_title, class_value in classes:
        class_id = get_class_id(class_title, class_value)
        if class_id:
            db.execute(sql, [movie_id, class_id])
    return movie_id


def update_movie(movie_id, movie_details, classes):
    title = movie_details["title"]
    year = movie_details["year"]
    duration = movie_details["duration"]
    director = movie_details["director"]
    language = movie_details["language"]
    main_actors = movie_details["main_actors"]
    imdb_url = movie_details["imdb_url"]

    sql = """UPDATE movies SET title = ?,
                               year = ?,
                               duration = ?,
                               director = ?,
                               language = ?,
                               main_actors = ?,
                               imdb_url = ?
                           WHERE id = ?"""
    db.execute(sql, [title, year, duration, director,
                     language, main_actors, imdb_url, movie_id])

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


def find_movies(search_params, page, page_size):
    sql = """SELECT DISTINCT m.id,
                             m.title,
                             m.user_id,
                             u.username,
                             COUNT(r.id) AS review_count
             FROM movies m
             LEFT JOIN movie_classes mc_genre ON m.id = mc_genre.movie_id
             LEFT JOIN classes c_genre ON mc_genre.class_id = c_genre.id AND c_genre.title = "genre"
             LEFT JOIN movie_classes mc_age ON m.id = mc_age.movie_id
             LEFT JOIN classes c_age ON mc_age.class_id = c_age.id AND c_age.title = "ikäraja"
             LEFT JOIN users u ON m.user_id = u.id
             LEFT JOIN reviews r ON m.id = r.movie_id
             WHERE 1=1"""

    params = []

    if search_params["query"]:
        sql += """ AND (
            m.title LIKE ?
            OR m.director LIKE ?
            OR m.language LIKE ?
            OR m.main_actors LIKE ?
            OR r.review LIKE ?
        )"""
        pattern = f"%{search_params["query"]}%"
        params += [pattern] * 5

    if search_params["min_grade"]:
        sql += " AND r.grade >= ?"
        params.append(search_params["min_grade"])

    if search_params["min_year"]:
        sql += " AND m.year >= ?"
        params.append(search_params["min_year"])

    if search_params["max_year"]:
        sql += " AND m.year <= ?"
        params.append(search_params["max_year"])

    if search_params["username"]:
        sql += " AND u.username LIKE ?"
        params.append(f"%{search_params["username"]}%")

    if search_params["genres"]:
        genre_list = [g.split(":")[1] if g.startswith("genre:")
                      else g for g in search_params["genres"].split(",")]
        placeholders = ",".join("?" * len(genre_list))
        sql += f" AND c_genre.value IN ({placeholders})"
        params.extend(genre_list)

    if search_params["age_limits"]:
        age_list = [a.split(":")[1] if a.startswith("ikäraja:")
                    else a for a in search_params["age_limits"].split(",")]
        placeholders = ",".join("?" * len(age_list))
        sql += f" AND c_age.value IN ({placeholders})"
        params.extend(age_list)

    sql += """ GROUP BY m.id, m.title, m.user_id
               ORDER BY m.id DESC
               LIMIT ? OFFSET ?"""

    limit = page_size
    offset = page_size * (page - 1)
    params += [limit, offset]

    return db.query(sql, params)


def count_found_movies(search_params):
    query = search_params["query"]
    min_grade = search_params["min_grade"]
    min_year = search_params["min_year"]
    max_year = search_params["max_year"]
    username = search_params["username"]
    genres = search_params["genres"]
    age_limits = search_params["age_limits"]

    sql = """SELECT COUNT(DISTINCT m.id) AS count
             FROM movies m
             LEFT JOIN movie_classes mc_genre ON m.id = mc_genre.movie_id
             LEFT JOIN classes c_genre ON mc_genre.class_id = c_genre.id AND c_genre.title = "genre"
             LEFT JOIN movie_classes mc_age ON m.id = mc_age.movie_id
             LEFT JOIN classes c_age ON mc_age.class_id = c_age.id AND c_age.title = "ikäraja"
             LEFT JOIN users u ON m.user_id = u.id
             LEFT JOIN reviews r ON m.id = r.movie_id
             WHERE 1=1"""

    params = []

    if query:
        sql += """ AND (
            m.title LIKE ?
            OR m.director LIKE ?
            OR m.language LIKE ?
            OR m.main_actors LIKE ?
            OR r.review LIKE ?
        )"""
        pattern = f"%{query}%"
        params += [pattern] * 5

    if min_grade:
        sql += " AND r.grade >= ?"
        params.append(min_grade)

    if min_year:
        sql += " AND m.year >= ?"
        params.append(min_year)

    if max_year:
        sql += " AND m.year <= ?"
        params.append(max_year)

    if username:
        sql += " AND u.username LIKE ?"
        params.append(f"%{username}%")

    if genres:
        genre_list = [g.split(":")[1] if g.startswith("genre:")
                      else g for g in genres.split(",")]
        placeholders = ",".join("?" * len(genre_list))
        sql += f" AND c_genre.value IN ({placeholders})"
        params.extend(genre_list)

    if age_limits:
        age_list = [a.split(":")[1] if a.startswith("ikäraja:")
                    else a for a in age_limits.split(",")]
        placeholders = ",".join("?" * len(age_list))
        sql += f" AND c_age.value IN ({placeholders})"
        params.extend(age_list)

    result = db.query(sql, params)
    return result[0]["count"] if result else 0
