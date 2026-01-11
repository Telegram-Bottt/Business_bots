-- add exceptions table for master schedules
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS master_exceptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  master_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  start_time TEXT,
  end_time TEXT,
  available INTEGER DEFAULT 1,
  note TEXT,
  FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE,
  UNIQUE(master_id, date)
);

CREATE TABLE IF NOT EXISTS master_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  master_id INTEGER NOT NULL,
  buffer_minutes INTEGER DEFAULT 0,
  timezone TEXT,
  FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE
);
