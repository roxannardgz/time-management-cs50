
/*
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


DROP TABLE IF EXISTS events;
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    start_ts TIMESTAMP NOT NULL,
    end_ts TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
*/

CREATE VIEW IF NOT EXISTS vw_events_clean AS 
    SELECT 
        event_id,
        user_id,
        category,
        subcategory,
        start_ts,
        end_ts,
        (unixepoch(end_ts) - unixepoch(start_ts))/60 AS duration_minutes
    FROM events
    WHERE end_ts IS NOT NULL;
