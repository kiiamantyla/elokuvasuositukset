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
    duration INTEGER,
    director TEXT,
    language TEXT,
    main_actors TEXT,
    imdb_url TEXT,
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


CREATE INDEX idx_reviews_movie_id ON reviews(movie_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);

CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_users_username ON users(username);

CREATE INDEX idx_movies_id ON movies(id);
CREATE INDEX idx_movies_user_id ON movies(user_id);
CREATE INDEX idx_movies_year ON movies(year);
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_director ON movies(director);
CREATE INDEX idx_movies_language ON movies(language);
CREATE INDEX idx_movies_main_actors ON movies(main_actors);

CREATE INDEX idx_movie_classes_movie_id ON movie_classes(movie_id);
CREATE INDEX idx_movie_classes_class_id ON movie_classes(class_id);

CREATE INDEX idx_classes_title_value ON classes(title, value);

CREATE INDEX idx_images_movie_id ON images(movie_id);
CREATE INDEX idx_posters_movie_id ON posters(movie_id);
