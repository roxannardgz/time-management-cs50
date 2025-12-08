
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    setup_completed INTEGER NOT NULL DEFAULT 0
);

DROP TABLE IF EXISTS user_activities;
CREATE TABLE user_activities (
    user_id INTEGER,
    category TEXT,
    subcategory TEXT,
    PRIMARY KEY (user_id, category, subcategory),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);



--CREATE TABLE events (

--);