-- SQLite init script for RespectCircle single-user demo state
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS metric;
DROP TABLE IF EXISTS user;

-- Create User table
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

-- Create Metric table
CREATE TABLE metric (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  weekly_goal INTEGER DEFAULT 300,
  daily_goal INTEGER DEFAULT 60,
  monthly_goal INTEGER DEFAULT 1200,
  weekly_played INTEGER DEFAULT 70,
  daily_played INTEGER DEFAULT 10,
  monthly_played INTEGER DEFAULT 210,
  high_score INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
);

-- Insert demo user
INSERT INTO user (username, password_hash) VALUES
('default_user', '$2b$12$eImiTXuWVxfM37uY4JANjQe5Jxq2p1uY8F5K9eK1EJ1o1o1o1o1o1');

-- Insert demo metrics
INSERT INTO metric (user_id, weekly_goal, daily_goal, monthly_goal, weekly_played, daily_played, monthly_played, high_score) VALUES
(1, 300, 60, 1200, 120, 30, 400, 7500);

PRAGMA foreign_keys = ON;
