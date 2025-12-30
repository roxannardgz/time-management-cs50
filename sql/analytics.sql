DROP VIEW IF EXISTS vw_daily_activity;
CREATE VIEW IF NOT EXISTS vw_daily_activity AS
SELECT
    user_id,
    event_date,
    weekday_num,
    category,
    subcategory,
    SUM(duration_seconds) AS total_seconds
FROM vw_events_facts_daily_split
GROUP BY user_id, event_date, weekday_num, category, subcategory;
