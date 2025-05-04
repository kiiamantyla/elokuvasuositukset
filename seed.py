import random
import sqlite3
import string

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM movies")
db.execute("DELETE FROM reviews")
db.execute("DELETE FROM movie_classes")
db.execute("DELETE FROM images")
db.execute("DELETE FROM posters")

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_name():
    first = random_string(5).capitalize()
    last = random_string(7).capitalize()
    return f"{first} {last}"

user_count = 1000
for _ in range(user_count):
    username = random_string()
    password_hash = random_string(64)
    db.execute("INSERT INTO users (username, password_hash, profile_picture) VALUES (?, ?, ?)",
               [username, password_hash, None])

genre_ids = [row[0] for row in db.execute("SELECT id FROM classes WHERE title = 'genre'")]
age_rating_ids = [row[0] for row in db.execute("SELECT id FROM classes WHERE title = 'ikäraja'")]

movie_count = 10**5
languages = ["English", "Finnish", "French", "Japanese", "Spanish"]
for _ in range(movie_count):
    title = "Movie " + random_string(6)
    year = random.randint(1950, 2025)
    duration = random.randint(60, 180)
    director = random_name()
    language = random.choice(languages)
    main_actors = ", ".join([random_name() for _ in range(3)])
    imdb_url = f"https://www.imdb.com/title/tt{random.randint(1000000, 9999999)}/"
    user_id = random.randint(1, user_count)

    cursor = db.execute("""INSERT INTO movies (title, year, duration, director, language,
                        main_actors, imdb_url, user_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        [title, year, duration, director, language, main_actors, imdb_url, user_id])

    movie_id = cursor.lastrowid

    genres = random.sample(genre_ids, k=random.randint(1, 3))
    for genre_id in genres:
        db.execute("""INSERT INTO movie_classes (movie_id, class_id)
                      VALUES (?, ?)""", [movie_id, genre_id])

    age_rating_id = random.choice(age_rating_ids)
    db.execute("INSERT INTO movie_classes (movie_id, class_id) VALUES (?, ?)",
               [movie_id, age_rating_id])

review_count = 10**4
for _ in range(review_count):
    movie_id = random.randint(1, movie_count)
    user_id = random.randint(1, user_count)
    review = " ".join([random_string(5) for _ in range(20)])
    grade = random.randint(1, 10)
    db.execute("INSERT INTO reviews (movie_id, user_id, review, grade) VALUES (?, ?, ?, ?)",
               [movie_id, user_id, review, grade])

for movie_id in range(1, movie_count + 1):
    db.execute("INSERT INTO images (movie_id, image) VALUES (?, ?)", [movie_id, None])
    db.execute("INSERT INTO posters (movie_id, poster) VALUES (?, ?)", [movie_id, None])

db.commit()
db.close()
