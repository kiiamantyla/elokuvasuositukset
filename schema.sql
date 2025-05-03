CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    profile_picture BLOB
);

CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT,
    year INTEGER,
    grade INTEGER,
    recommendation TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    user_id INTEGER REFERENCES users,
    review TEXT,
    grade INTEGER
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE movie_classes (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    class_id INTEGER REFERENCES classes,
    UNIQUE(movie_id, class_id)
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    image BLOB
);

CREATE TABLE posters (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER REFERENCES movies,
    poster BLOB
);
