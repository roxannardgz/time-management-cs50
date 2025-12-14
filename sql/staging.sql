DROP VIEW vw_events_facts;
CREATE VIEW IF NOT EXISTS vw_events_facts AS 
    SELECT 
        event_id,
        user_id,
        category,
        subcategory,
        --substr('SunMonTueWedThuFriSat', 1 + 3*strftime('%w', start_ts), 3) AS day_of_week,
        strftime('%w', start_ts) AS weekday_num,
        DATE(start_ts) AS event_date,
        TIME(start_ts) AS start_time,
        TIME(end_ts) AS end_time,
        --unixepoch(end_ts) - unixepoch(start_ts) AS duration_seconds,
        strftime('%s', end_ts) - strftime('%s', start_ts) AS duration_seconds
    FROM events
    WHERE end_ts IS NOT NULL;