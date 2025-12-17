DROP VIEW IF EXISTS vw_events_facts;
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

------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_events_facts_daily_split;
CREATE VIEW IF NOT EXISTS vw_events_facts_daily_split AS
-- full duration if same-day, else until midnight
SELECT
  event_id,
  user_id,
  category,
  subcategory,
  DATE(start_ts) AS event_date,
  strftime('%w', start_ts) AS weekday_num,
  CASE
    WHEN DATE(start_ts) = DATE(end_ts)
      THEN strftime('%s', end_ts) - strftime('%s', start_ts)
    ELSE
      strftime('%s', DATETIME(DATE(start_ts), '+1 day')) - strftime('%s', start_ts)
  END AS duration_seconds
FROM events
WHERE end_ts IS NOT NULL

UNION ALL

-- when it crosses midnight (midnight -> end)
SELECT
  event_id,
  user_id,
  category,
  subcategory,
  DATE(end_ts) AS event_date,
  strftime('%w', end_ts) AS weekday_num,
  strftime('%s', end_ts) - strftime('%s', DATETIME(DATE(end_ts))) AS duration_seconds
FROM events
WHERE end_ts IS NOT NULL
  AND DATE(start_ts) <> DATE(end_ts);
