-- SQLite init script for RespectCircle single-user demo state
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS metric;

-- Create Metric table (single row)
CREATE TABLE metric (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  weekly_goal INTEGER DEFAULT 300,
  daily_goal INTEGER DEFAULT 60,
  monthly_goal INTEGER DEFAULT 1200,
  weekly_played INTEGER DEFAULT 0,
  daily_played INTEGER DEFAULT 0,
  monthly_played INTEGER DEFAULT 0,
  high_score INTEGER DEFAULT 0
);

-- Insert demo metrics
INSERT INTO metric (weekly_goal, daily_goal, monthly_goal, weekly_played, daily_played, monthly_played, high_score) VALUES
(300, 60, 1200, 120, 30, 400, 7500);

PRAGMA foreign_keys = ON;
